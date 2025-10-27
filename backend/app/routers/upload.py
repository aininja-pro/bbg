"""API endpoints for file upload and processing."""
import os
import tempfile
import uuid
import zipfile
import gc
import base64
import time
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from fastapi.responses import FileResponse, StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
import io
import pandas as pd

from app.database import get_db
from app.services.pipeline import ProcessingPipeline
from app.config import settings
from app.repositories.processed_file import ProcessedFileRepository
from app.schemas.processed_file import ProcessedFileCreate, ProcessedFileResponse, ProcessedFileStatus
from app.models.processed_file import ProcessedFile

router = APIRouter(prefix="/api", tags=["File Processing"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process a single rebate Excel file.

    Returns processing results with preview data and warnings.
    """
    # Validate file type
    if not file.filename.endswith(('.xlsm', '.xlsx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only .xlsm and .xlsx files are supported."
        )

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB."
        )

    # Save uploaded file temporarily
    temp_file_path = None
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsm') as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)

        # Process the file
        pipeline = ProcessingPipeline(db)
        result = await pipeline.process_file(temp_file_path)

        if result['success']:
            return {
                "success": True,
                "message": "File processed successfully",
                "data": {
                    "member_name": result['metadata']['member_name'],
                    "bbg_member_id": result['metadata']['bbg_member_id'],
                    "total_rows": result['total_rows'],
                    "active_products": result['active_products'],
                    "preview": result['preview'],  # All rows for frontend pagination
                    "warnings": result['warnings']
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File processing failed: {result.get('error', 'Unknown error')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error processing file: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.post("/process-and-download")
async def process_and_download(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload, process, and immediately download the result as CSV.

    Returns a CSV file ready for FMS import.
    """
    # Validate file type
    if not file.filename.endswith(('.xlsm', '.xlsx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only .xlsm and .xlsx files are supported."
        )

    temp_file_path = None
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsm') as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)

        # Process the file
        pipeline = ProcessingPipeline(db)
        result = await pipeline.process_file(temp_file_path)

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Processing failed: {result.get('error')}"
            )

        # Get DataFrame and convert to CSV
        df = pipeline.get_dataframe()

        # Create CSV in memory
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        # Generate filename
        member_name = result['metadata']['member_name'].replace(' ', '_')
        bbg_id = result['metadata']['bbg_member_id']
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{member_name}_{bbg_id}_{timestamp}.csv"

        # Return as streaming response
        return StreamingResponse(
            iter([csv_buffer.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.post("/batch-process")
async def batch_process(
    files: List[UploadFile] = File(...),
    output_mode: str = "zip",  # "zip" or "merged" via query parameter
    db: AsyncSession = Depends(get_db)
):
    """Process multiple Excel files at once with memory-efficient streaming.

    Optimized for processing up to 50 files on limited memory environments (512MB RAM).
    Files are processed one at a time and immediately written to output to minimize
    memory footprint.

    Args:
        files: List of Excel files to process
        output_mode: "zip" for individual CSVs in ZIP, "merged" for single combined CSV

    Returns:
        ZIP file with individual CSVs OR single merged CSV
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )

    # Check batch size limit
    if len(files) > settings.MAX_BATCH_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many files. Maximum batch size is {settings.MAX_BATCH_FILES} files."
        )

    # Validate all files
    for file in files:
        if not file.filename.endswith(('.xlsm', '.xlsx')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {file.filename}. Only .xlsm and .xlsx files are supported."
            )

    temp_files = []

    try:
        if output_mode == "merged":
            # Memory-efficient merged mode: process and concatenate one at a time
            merged_chunks = []
            successful_count = 0

            for file in files:
                # Save temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsm') as temp_file:
                    temp_path = temp_file.name
                    temp_files.append(temp_path)
                    content = await file.read()
                    temp_file.write(content)

                # Process file - disable preview to reduce memory
                pipeline = ProcessingPipeline(db)
                result = await pipeline.process_file(temp_path, include_preview=False)

                if result['success']:
                    df = pipeline.get_dataframe()
                    merged_chunks.append(df)
                    successful_count += 1

                # Force cleanup of pipeline and temp variables
                del pipeline
                if 'df' in locals():
                    del df
                gc.collect()

                # Delete temp file immediately after processing
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                        temp_files.remove(temp_path)
                    except:
                        pass

            if not merged_chunks:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No files were successfully processed"
                )

            # Concatenate all chunks
            merged_df = pd.concat(merged_chunks, ignore_index=True)

            # Clear chunks from memory
            del merged_chunks
            gc.collect()

            # Create CSV
            csv_buffer = io.StringIO()
            merged_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            filename = f"Batch_Merged_{successful_count}_files_{timestamp}.csv"

            # Clear merged_df from memory before returning
            del merged_df
            gc.collect()

            return StreamingResponse(
                iter([csv_buffer.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )

        else:  # output_mode == "zip" - MEMORY OPTIMIZED
            # Stream directly to ZIP without holding all DataFrames in memory
            zip_buffer = io.BytesIO()
            successful_count = 0
            failed_files = []

            with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
                for file in files:
                    temp_path = None
                    try:

                        # Save temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsm') as temp_file:
                            temp_path = temp_file.name
                            temp_files.append(temp_path)
                            content = await file.read()
                            temp_file.write(content)

                        # Process file - disable preview to reduce memory
                        pipeline = ProcessingPipeline(db)
                        result = await pipeline.process_file(temp_path, include_preview=False)

                        if result['success']:
                            # Get DataFrame and immediately convert to CSV
                            df = pipeline.get_dataframe()
                            csv_data = df.to_csv(index=False)

                            # Generate filename and add to ZIP
                            original_name = file.filename.replace('.xlsm', '').replace('.xlsx', '')
                            csv_filename = f"{original_name}_processed.csv"

                            # Write to ZIP immediately
                            zip_file.writestr(csv_filename, csv_data.encode('utf-8'))
                            successful_count += 1

                            # Free memory immediately
                            del df
                            del csv_data
                        else:
                            failed_files.append({
                                'filename': file.filename,
                                'error': result.get('error', 'Unknown error')
                            })

                        # Cleanup pipeline and force garbage collection
                        del pipeline
                        gc.collect()

                        # Delete temp file immediately after processing
                        if temp_path and os.path.exists(temp_path):
                            try:
                                os.unlink(temp_path)
                                temp_files.remove(temp_path)
                            except:
                                pass

                    except Exception as file_error:
                        failed_files.append({
                            'filename': file.filename,
                            'error': str(file_error)
                        })
                        continue

                # If there were failures, add an error log to the ZIP
                if failed_files:
                    error_log = "Failed Files:\n" + "\n".join(
                        [f"- {f['filename']}: {f['error']}" for f in failed_files]
                    )
                    zip_file.writestr("_ERRORS.txt", error_log.encode('utf-8'))

            # Get the full bytes AFTER closing the ZIP
            zip_bytes = zip_buffer.getvalue()

            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            zip_filename = f"Batch_Processed_{successful_count}_files_{timestamp}.zip"

            return StreamingResponse(
                io.BytesIO(zip_bytes),
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename={zip_filename}"
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch processing error: {str(e)}"
        )
    finally:
        # Clean up all temp files
        for temp_path in temp_files:
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass  # Ignore cleanup errors

        # Final garbage collection
        gc.collect()


# NEW CACHED ENDPOINTS FOR FAST DOWNLOADS


@router.post("/upload-with-cache", response_model=ProcessedFileStatus)
async def upload_file_with_cache(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process a single rebate Excel file, caching the result for fast downloads.

    Returns a job_id that can be used to download the processed CSV instantly.
    """
    # Validate file type
    if not file.filename.endswith(('.xlsm', '.xlsx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only .xlsm and .xlsx files are supported."
        )

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB."
        )

    # Generate unique job_id
    job_id = str(uuid.uuid4())

    # Create initial database record
    processed_file_data = ProcessedFileCreate(
        job_id=job_id,
        filename=file.filename,
        original_filenames=[file.filename],
        file_type='single',
        status='processing',
        expires_at=ProcessedFile.calculate_expiration(24)
    )

    await ProcessedFileRepository.create(db, processed_file_data)

    temp_file_path = None
    start_time = time.time()

    try:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsm') as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)

        # Process the file
        pipeline = ProcessingPipeline(db)
        result = await pipeline.process_file(temp_file_path, include_preview=False)

        if result['success']:
            # Get the processed DataFrame
            df = pipeline.get_dataframe()

            # Convert to CSV string
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()

            # Calculate metrics
            processing_time = int(time.time() - start_time)
            total_rows = len(df)
            file_size_bytes = len(csv_data.encode('utf-8'))

            # Update database with processed data
            await ProcessedFileRepository.update_processed_data(
                db=db,
                job_id=job_id,
                processed_data=csv_data,
                total_rows=total_rows,
                file_size_bytes=file_size_bytes,
                processing_time_seconds=processing_time,
                processing_metadata=result['metadata']
            )

            return ProcessedFileStatus(
                job_id=job_id,
                status='completed',
                filename=file.filename,
                created_at=datetime.utcnow()
            )
        else:
            # Mark as failed
            error_msg = result.get('error', 'Unknown error')
            await ProcessedFileRepository.update_status(db, job_id, 'failed', error_msg)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File processing failed: {error_msg}"
            )

    except HTTPException:
        raise
    except Exception as e:
        # Mark as failed
        await ProcessedFileRepository.update_status(db, job_id, 'failed', str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error processing file: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.post("/batch-process-with-cache", response_model=ProcessedFileStatus)
async def batch_process_with_cache(
    files: List[UploadFile] = File(...),
    output_mode: str = Query(default="merged", regex="^(zip|merged)$"),
    db: AsyncSession = Depends(get_db)
):
    """Process multiple Excel files and cache the result (merged CSV or ZIP).

    Returns a job_id that can be used to download the result instantly.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )

    if len(files) > settings.MAX_BATCH_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many files. Maximum batch size is {settings.MAX_BATCH_FILES} files."
        )

    # Validate all files
    for file in files:
        if not file.filename.endswith(('.xlsm', '.xlsx')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {file.filename}"
            )

    # Generate unique job_id
    job_id = str(uuid.uuid4())

    # Create initial database record
    filenames = [f.filename for f in files]
    batch_filename = f"Batch_{len(files)}_files_{'merged' if output_mode == 'merged' else 'zip'}.{'csv' if output_mode == 'merged' else 'zip'}"

    processed_file_data = ProcessedFileCreate(
        job_id=job_id,
        filename=batch_filename,
        original_filenames=filenames,
        file_type=f'batch_{output_mode}',
        status='processing',
        expires_at=ProcessedFile.calculate_expiration(24)
    )

    await ProcessedFileRepository.create(db, processed_file_data)

    temp_files = []
    start_time = time.time()

    try:
        if output_mode == "merged":
            # Process and merge all files
            merged_chunks = []

            for file in files:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsm') as temp_file:
                    temp_path = temp_file.name
                    temp_files.append(temp_path)
                    content = await file.read()
                    temp_file.write(content)

                pipeline = ProcessingPipeline(db)
                result = await pipeline.process_file(temp_path, include_preview=False)

                if result['success']:
                    df = pipeline.get_dataframe()
                    merged_chunks.append(df)

                del pipeline
                gc.collect()

            if not merged_chunks:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No files were successfully processed"
                )

            # Merge all DataFrames
            merged_df = pd.concat(merged_chunks, ignore_index=True)
            del merged_chunks
            gc.collect()

            # Convert to CSV
            csv_buffer = io.StringIO()
            merged_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()

            processing_time = int(time.time() - start_time)

            # Update database
            await ProcessedFileRepository.update_processed_data(
                db=db,
                job_id=job_id,
                processed_data=csv_data,
                total_rows=len(merged_df),
                file_size_bytes=len(csv_data.encode('utf-8')),
                processing_time_seconds=processing_time
            )

        else:  # output_mode == "zip"
            # Process files and create ZIP
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsm') as temp_file:
                        temp_path = temp_file.name
                        temp_files.append(temp_path)
                        content = await file.read()
                        temp_file.write(content)

                    pipeline = ProcessingPipeline(db)
                    result = await pipeline.process_file(temp_path, include_preview=False)

                    if result['success']:
                        df = pipeline.get_dataframe()
                        csv_buffer = io.StringIO()
                        df.to_csv(csv_buffer, index=False)
                        csv_content = csv_buffer.getvalue()

                        # Add to ZIP
                        csv_filename = file.filename.replace('.xlsm', '.csv').replace('.xlsx', '.csv')
                        zipf.writestr(csv_filename, csv_content)

                    del pipeline
                    gc.collect()

            # Get ZIP bytes and encode as base64 for storage
            zip_bytes = zip_buffer.getvalue()
            zip_base64 = base64.b64encode(zip_bytes).decode('utf-8')

            processing_time = int(time.time() - start_time)

            # Update database
            await ProcessedFileRepository.update_processed_data(
                db=db,
                job_id=job_id,
                processed_data=zip_base64,  # Store as base64
                total_rows=None,  # Not applicable for ZIP
                file_size_bytes=len(zip_bytes),
                processing_time_seconds=processing_time
            )

        return ProcessedFileStatus(
            job_id=job_id,
            status='completed',
            filename=batch_filename,
            created_at=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        await ProcessedFileRepository.update_status(db, job_id, 'failed', str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch processing error: {str(e)}"
        )
    finally:
        # Clean up temp files
        for temp_path in temp_files:
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
        gc.collect()


@router.get("/download/{job_id}")
async def download_by_job_id(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Download a processed file by job_id (instant retrieval from cache)."""

    # Get processed file from database
    processed_file = await ProcessedFileRepository.get_by_job_id(db, job_id)

    if not processed_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or expired"
        )

    if processed_file.status == 'processing':
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="File is still processing. Please try again in a moment."
        )

    if processed_file.status == 'failed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Processing failed: {processed_file.error_message}"
        )

    # Check if expired
    if processed_file.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This file has expired and is no longer available"
        )

    # Record download
    await ProcessedFileRepository.record_download(db, job_id)

    # Return the cached data
    if processed_file.file_type == 'batch_zip':
        # Decode base64 ZIP
        zip_bytes = base64.b64decode(processed_file.processed_data)

        return StreamingResponse(
            io.BytesIO(zip_bytes),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={processed_file.filename}"
            }
        )
    else:
        # Return CSV (single or merged)
        return StreamingResponse(
            io.StringIO(processed_file.processed_data),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={processed_file.filename}"
            }
        )


@router.get("/job-status/{job_id}", response_model=ProcessedFileStatus)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Check the status of a processing job."""

    processed_file = await ProcessedFileRepository.get_by_job_id(db, job_id)

    if not processed_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return ProcessedFileStatus(
        job_id=processed_file.job_id,
        status=processed_file.status,
        filename=processed_file.filename,
        created_at=processed_file.created_at,
        error_message=processed_file.error_message
    )


@router.delete("/cleanup-expired")
async def cleanup_expired_files(db: AsyncSession = Depends(get_db)):
    """Manually trigger cleanup of expired processed files."""

    deleted_count = await ProcessedFileRepository.delete_expired(db)

    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": f"Deleted {deleted_count} expired files"
    }
