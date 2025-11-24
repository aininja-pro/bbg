"""API endpoints for supplier and territory manager report distribution."""
import uuid
import base64
import asyncio
import tempfile
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, AsyncSessionLocal
from app.models.processed_file import ProcessedFile
from app.services.report_generator import ReportGenerator
from app.repositories.processed_file import ProcessedFileRepository
from app.schemas.processed_file import ProcessedFileCreate, ProcessedFileResponse, ProcessedFileStatus

router = APIRouter(prefix="/api/distribution", tags=["Distribution"])


@router.post("/process")
async def process_distribution(
    files: List[UploadFile] = File(...),
    mode: str = Query(..., regex="^(mode1|mode2)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Process uploaded CSV files and generate supplier/TM distribution reports.

    Mode 1: Supplier with Product tabs (Supplier_With_Product_Tabs.xlsx structure)
    Mode 2: TM with Supplier tabs (TM_with_Supplier_Tabs.xlsx structure)

    Returns:
        job_id: UUID for downloading the generated ZIP file
        status: Processing status
    """
    # Validate files
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded"
        )

    for file in files:
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} must be a CSV file"
            )

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Collect original filenames
    original_filenames = [file.filename for file in files]

    # Create initial processed file record
    file_data = ProcessedFileCreate(
        job_id=job_id,
        filename=f"{mode}_distribution_{job_id}.zip",
        original_filenames=original_filenames,
        file_type=f"distribution_{mode}",
        status="processing",
        total_rows=0,
        file_size_bytes=0,
        processing_metadata={"mode": mode},
        expires_at=ProcessedFile.calculate_expiration(24)
    )

    await ProcessedFileRepository.create(db, file_data)

    # Process files in background - create new DB session for background task
    asyncio.create_task(
        _process_distribution_task(job_id, files, mode)
    )

    return {
        "job_id": job_id,
        "status": "processing",
        "message": f"Distribution processing started for {len(files)} file(s)"
    }


async def _process_distribution_task(
    job_id: str,
    files: List[UploadFile],
    mode: str
):
    """
    Background task to process distribution reports.

    Args:
        job_id: Job ID for tracking
        files: List of uploaded CSV files
        mode: "mode1" or "mode2"
    """
    temp_files = []

    # Create new database session for background task
    async with AsyncSessionLocal() as db:
        try:
            # Progress callback to update database
            async def update_progress(percentage: int, message: str):
                await ProcessedFileRepository.update_status(
                    db=db,
                    job_id=job_id,
                    status="processing",
                    error_message=None
                )
                # Update metadata with progress
                processed_file = await ProcessedFileRepository.get_by_job_id(db, job_id)
                if processed_file:
                    metadata = processed_file.processing_metadata or {}
                    metadata['progress'] = percentage
                    metadata['progress_message'] = message
                    # Quick update (without full update_processed_data call)
                    from sqlalchemy import update
                    from app.models.processed_file import ProcessedFile as ProcessedFileModel
                    await db.execute(
                        update(ProcessedFileModel)
                        .where(ProcessedFileModel.job_id == job_id)
                        .values(processing_metadata=metadata)
                    )
                    await db.commit()

            # Update: 0% - Saving files
            await update_progress(0, "Saving uploaded files...")

            # Save uploaded files to temporary directory
            temp_dir = tempfile.mkdtemp()

            for file in files:
                temp_path = os.path.join(temp_dir, file.filename)
                contents = await file.read()

                with open(temp_path, 'wb') as f:
                    f.write(contents)

                temp_files.append(temp_path)

            # Update: 5% - Merging CSVs
            await update_progress(5, "Merging CSV files...")

            # Merge CSV files
            merged_df = await ReportGenerator.merge_csv_files(temp_files)

            total_rows = len(merged_df)

            # Update: 10% - Analyzing data
            await update_progress(10, f"Analyzing data... ({total_rows:,} rows)")

            # Update: 15% - Starting generation
            await update_progress(15, "Starting report generation...")

            # Generate distribution ZIP with progress tracking (15-100%)
            zip_bytes = await ReportGenerator.create_distribution_zip(
                mode=mode,
                df=merged_df,
                db=db if mode == "mode2" else None,
                progress_callback=lambda pct, msg: update_progress(15 + int(pct * 0.85), msg)
            )

            # Encode ZIP as base64 for storage
            zip_base64 = base64.b64encode(zip_bytes).decode('utf-8')

            # Update processed file record with results
            await ProcessedFileRepository.update_processed_data(
                db=db,
                job_id=job_id,
                processed_data=zip_base64,
                total_rows=total_rows,
                file_size_bytes=len(zip_bytes),
                processing_time_seconds=0,  # Could track this if needed
                processing_metadata={"mode": mode, "file_count": len(files)}
            )

            await ProcessedFileRepository.update_status(
                db=db,
                job_id=job_id,
                status="completed"
            )

        except Exception as e:
            # Update status to failed
            error_message = str(e)
            await ProcessedFileRepository.update_status(
                db=db,
                job_id=job_id,
                status="failed",
                error_message=error_message
            )

        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass

            # Clean up temp directory
            try:
                if 'temp_dir' in locals():
                    os.rmdir(temp_dir)
            except:
                pass


@router.get("/status/{job_id}")
async def get_distribution_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the status of a distribution processing job.

    Args:
        job_id: Job ID to check

    Returns:
        Status information including progress and any errors
    """
    processed_file = await ProcessedFileRepository.get_by_job_id(db, job_id)

    if not processed_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    return {
        "job_id": processed_file.job_id,
        "status": processed_file.status,
        "filename": processed_file.filename,
        "total_rows": processed_file.total_rows,
        "file_size_bytes": processed_file.file_size_bytes,
        "error_message": processed_file.error_message,
        "created_at": processed_file.created_at.isoformat() if processed_file.created_at else None,
        "expires_at": processed_file.expires_at.isoformat() if processed_file.expires_at else None,
        "metadata": processed_file.processing_metadata
    }


@router.get("/download/{job_id}")
async def download_distribution(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Download the generated distribution ZIP file.

    Args:
        job_id: Job ID to download

    Returns:
        ZIP file containing all Excel files
    """
    processed_file = await ProcessedFileRepository.get_by_job_id(db, job_id)

    if not processed_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    if processed_file.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job {job_id} is not completed (status: {processed_file.status})"
        )

    if not processed_file.processed_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data available for job {job_id}"
        )

    # Decode base64 ZIP data
    try:
        zip_bytes = base64.b64decode(processed_file.processed_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decode ZIP data: {str(e)}"
        )

    # Record download
    await ProcessedFileRepository.record_download(db, job_id)

    # Return ZIP file
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={processed_file.filename}"
        }
    )
