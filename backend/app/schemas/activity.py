"""Pydantic schemas for activity logging."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ActivityStatus(str, Enum):
    """Activity log status types."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PROCESSING = "processing"


class ActivityLogCreate(BaseModel):
    """Schema for creating an Activity Log."""
    run_id: str = Field(..., max_length=100)
    status: ActivityStatus
    input_files: Optional[List[str]] = None
    members_processed: int = Field(default=0, ge=0)
    total_rows_processed: int = Field(default=0, ge=0)
    total_rows_output: int = Field(default=0, ge=0)
    warnings: Optional[List[str]] = None
    errors: Optional[List[str]] = None
    duration_seconds: Optional[int] = Field(None, ge=0)
    details: Optional[Dict[str, Any]] = None


class ActivityLogResponse(BaseModel):
    """Schema for Activity Log response."""
    id: int
    run_id: str
    run_timestamp: datetime
    status: ActivityStatus
    input_files: Optional[List[str]]
    members_processed: int
    total_rows_processed: int
    total_rows_output: int
    warnings: Optional[List[str]]
    errors: Optional[List[str]]
    duration_seconds: Optional[int]
    details: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivityLogFilter(BaseModel):
    """Schema for filtering activity logs."""
    status: Optional[ActivityStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
