"""Pydantic schemas for settings."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SettingsBase(BaseModel):
    """Base settings schema."""
    setting_key: str
    setting_value: Dict[str, Any]
    description: Optional[str] = None


class SettingsCreate(SettingsBase):
    """Schema for creating settings."""
    pass


class SettingsUpdate(BaseModel):
    """Schema for updating settings."""
    setting_value: Dict[str, Any]
    description: Optional[str] = None


class SettingsResponse(SettingsBase):
    """Schema for settings response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ColumnSettingsBase(BaseModel):
    """Base column settings schema."""
    column_name: str
    enabled: bool = True
    display_order: int = 0
    is_custom: bool = False
    description: Optional[str] = None


class ColumnSettingsCreate(ColumnSettingsBase):
    """Schema for creating column settings."""
    pass


class ColumnSettingsUpdate(BaseModel):
    """Schema for updating column settings."""
    enabled: Optional[bool] = None
    display_order: Optional[int] = None
    description: Optional[str] = None


class ColumnSettingsResponse(ColumnSettingsBase):
    """Schema for column settings response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BulkColumnSettingsUpdate(BaseModel):
    """Schema for bulk updating column settings."""
    columns: List[Dict[str, Any]] = Field(
        ...,
        description="List of column settings to update",
        example=[
            {"column_name": "member_name", "enabled": True, "display_order": 1},
            {"column_name": "bbg_member_id", "enabled": True, "display_order": 2}
        ]
    )
