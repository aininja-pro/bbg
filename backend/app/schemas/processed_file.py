"""Pydantic schemas for processed file validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProcessedFileCreate(BaseModel):
    """Schema for creating a processed file record."""
    job_id: str = Field(..., max_length=100)
    filename: str = Field(..., max_length=500)
    original_filenames: Optional[list[str]] = None
    file_type: str = Field(..., max_length=50)  # 'single', 'batch_merged', 'batch_zip'
    status: str = Field(default='processing', max_length=50)
    processed_data: Optional[str] = None
    total_rows: Optional[int] = None
    file_size_bytes: Optional[int] = None
    processing_time_seconds: Optional[int] = None
    metadata: Optional[dict] = None
    error_message: Optional[str] = None
    expires_at: datetime


class ProcessedFileResponse(BaseModel):
    """Schema for processed file response."""
    id: int
    job_id: str
    filename: str
    original_filenames: Optional[list[str]]
    file_type: str
    status: str
    total_rows: Optional[int]
    file_size_bytes: Optional[int]
    processing_time_seconds: Optional[int]
    metadata: Optional[dict]
    error_message: Optional[str]
    created_at: datetime
    expires_at: datetime
    last_downloaded_at: Optional[datetime]
    download_count: int

    model_config = ConfigDict(from_attributes=True)


class ProcessedFileStatus(BaseModel):
    """Schema for checking processed file status."""
    job_id: str
    status: str
    filename: str
    created_at: datetime
    error_message: Optional[str] = None
