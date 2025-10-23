"""API endpoints for file upload and processing."""
import os
import tempfile
import uuid
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
