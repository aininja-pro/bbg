"""API endpoints for file upload and processing."""
import os
import tempfile
import uuid
import zipfile
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io
import pandas as pd

from app.database import get_db
from app.services.pipeline import ProcessingPipeline
from app.config import settings

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
    """Process multiple Excel files at once.

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
    processed_results = []

    try:
        # Process each file
        for file in files:
            # Save temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsm') as temp_file:
                temp_path = temp_file.name
                temp_files.append(temp_path)
                content = await file.read()
                temp_file.write(content)

            # Process file
            pipeline = ProcessingPipeline(db)
            result = await pipeline.process_file(temp_path)

            if result['success']:
                df = pipeline.get_dataframe()
                processed_results.append({
                    'filename': file.filename,
                    'df': df,
                    'metadata': result['metadata'],
                    'rows': result['total_rows']
                })
            else:
                # If any file fails, include it in response but continue
                processed_results.append({
                    'filename': file.filename,
                    'error': result.get('error', 'Unknown error'),
                    'rows': 0
                })

        # Generate output based on mode
        if output_mode == "merged":
            # Merge all successful DataFrames into one CSV
            dfs_to_merge = [r['df'] for r in processed_results if 'df' in r]

            if not dfs_to_merge:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No files were successfully processed"
                )

            merged_df = pd.concat(dfs_to_merge, ignore_index=True)

            # Create CSV
            csv_buffer = io.StringIO()
            merged_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            filename = f"Batch_Merged_{len(dfs_to_merge)}_files_{timestamp}.csv"

            return StreamingResponse(
                iter([csv_buffer.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )

        else:  # output_mode == "zip"
            # Create ZIP file with individual CSVs
            zip_buffer = io.BytesIO()

            # Create ZIP and write CSV files
            with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
                for result in processed_results:
                    if 'df' in result:
                        # Create CSV for this file
                        csv_data = result['df'].to_csv(index=False)

                        # Generate filename
                        original_name = result['filename'].replace('.xlsm', '').replace('.xlsx', '')
                        csv_filename = f"{original_name}_processed.csv"

                        # Add to ZIP - encode as bytes
                        zip_file.writestr(csv_filename, csv_data.encode('utf-8'))

            # Get the full bytes AFTER closing the ZIP
            zip_bytes = zip_buffer.getvalue()

            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            zip_filename = f"Batch_Processed_{len(processed_results)}_files_{timestamp}.zip"

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
                os.unlink(temp_path)


