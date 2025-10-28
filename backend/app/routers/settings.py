"""API endpoints for settings management."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.settings import Settings, ColumnSettings
from app.repositories.settings import SettingsRepository, ColumnSettingsRepository
from app.schemas.settings import (
    SettingsResponse,
    SettingsCreate,
    SettingsUpdate,
    ColumnSettingsResponse,
    ColumnSettingsCreate,
    ColumnSettingsUpdate,
    BulkColumnSettingsUpdate,
)

router = APIRouter(prefix="/api/settings", tags=["Settings"])


# ==================== General Settings ====================

@router.get("", response_model=List[SettingsResponse])
async def get_all_settings(db: AsyncSession = Depends(get_db)):
    """Get all settings."""
    settings = await SettingsRepository.get_all(db)
    return settings


@router.get("/{setting_key}", response_model=SettingsResponse)
async def get_setting(setting_key: str, db: AsyncSession = Depends(get_db)):
    """Get setting by key."""
    setting = await SettingsRepository.get_by_key(db, setting_key)
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{setting_key}' not found",
        )
    return setting


@router.post("", response_model=SettingsResponse, status_code=status.HTTP_201_CREATED)
async def create_setting(
    setting: SettingsCreate, db: AsyncSession = Depends(get_db)
):
    """Create new setting."""
    # Check if setting already exists
    existing = await SettingsRepository.get_by_key(db, setting.setting_key)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Setting '{setting.setting_key}' already exists",
        )
    return await SettingsRepository.create(db, setting)


@router.put("/{setting_key}", response_model=SettingsResponse)
async def update_setting(
    setting_key: str, setting: SettingsUpdate, db: AsyncSession = Depends(get_db)
):
    """Update existing setting or create if doesn't exist."""
    updated = await SettingsRepository.upsert(
        db, setting_key, setting.setting_value, setting.description
    )
    return updated


# ==================== Column Settings ====================

@router.get("/columns/all", response_model=List[ColumnSettingsResponse])
async def get_all_columns(db: AsyncSession = Depends(get_db)):
    """Get all column settings."""
    columns = await ColumnSettingsRepository.get_all(db)
    return columns


@router.get("/columns/enabled", response_model=List[ColumnSettingsResponse])
async def get_enabled_columns(db: AsyncSession = Depends(get_db)):
    """Get all enabled column settings."""
    columns = await ColumnSettingsRepository.get_enabled(db)
    return columns


@router.get("/columns/{column_name}", response_model=ColumnSettingsResponse)
async def get_column(column_name: str, db: AsyncSession = Depends(get_db)):
    """Get column setting by name."""
    column = await ColumnSettingsRepository.get_by_name(db, column_name)
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column '{column_name}' not found",
        )
    return column


@router.post(
    "/columns", response_model=ColumnSettingsResponse, status_code=status.HTTP_201_CREATED
)
async def create_column(
    column: ColumnSettingsCreate, db: AsyncSession = Depends(get_db)
):
    """Create new column setting."""
    # Check if column already exists
    existing = await ColumnSettingsRepository.get_by_name(db, column.column_name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Column '{column.column_name}' already exists",
        )
    return await ColumnSettingsRepository.create(db, column)


@router.put("/columns/{column_name}", response_model=ColumnSettingsResponse)
async def update_column(
    column_name: str, column: ColumnSettingsUpdate, db: AsyncSession = Depends(get_db)
):
    """Update existing column setting."""
    updated = await ColumnSettingsRepository.update(db, column_name, column)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column '{column_name}' not found",
        )
    return updated


@router.post("/columns/bulk", response_model=List[ColumnSettingsResponse])
async def bulk_update_columns(
    data: BulkColumnSettingsUpdate, db: AsyncSession = Depends(get_db)
):
    """Bulk update column settings."""
    columns = await ColumnSettingsRepository.bulk_upsert(db, data.columns)
    return columns


@router.delete("/columns/{column_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(column_name: str, db: AsyncSession = Depends(get_db)):
    """Delete column setting."""
    deleted = await ColumnSettingsRepository.delete(db, column_name)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Column '{column_name}' not found",
        )


@router.post("/columns/initialize", response_model=List[ColumnSettingsResponse])
async def initialize_columns(db: AsyncSession = Depends(get_db)):
    """Initialize default column settings."""
    # Default columns in order
    default_columns = [
        {"column_name": "member_name", "enabled": True, "display_order": 1, "description": "BBG member company name"},
        {"column_name": "bbg_member_id", "enabled": True, "display_order": 2, "description": "TradeNet member ID"},
        {"column_name": "confirmed_occupancy", "enabled": True, "display_order": 3, "description": "Occupancy date"},
        {"column_name": "job_code", "enabled": True, "display_order": 4, "description": "Job or project identifier"},
        {"column_name": "address1", "enabled": True, "display_order": 5, "description": "Street address"},
        {"column_name": "city", "enabled": True, "display_order": 6, "description": "City name"},
        {"column_name": "state", "enabled": True, "display_order": 7, "description": "Two-letter state code"},
        {"column_name": "zip_postal", "enabled": True, "display_order": 8, "description": "Zip code"},
        {"column_name": "address_type", "enabled": True, "display_order": 9, "description": "RESIDENTIAL or COMMERCIAL"},
        {"column_name": "quantity", "enabled": True, "display_order": 10, "description": "Quantity of items"},
        {"column_name": "product_id", "enabled": True, "display_order": 11, "description": "TradeNet product ID"},
        {"column_name": "supplier_name", "enabled": True, "display_order": 12, "description": "Supplier company name"},
        {"column_name": "tradenet_supplier_id", "enabled": True, "display_order": 13, "description": "TradeNet supplier ID"},
        # New proof point fields (disabled by default until we know where data comes from)
        {"column_name": "pp_receipt", "enabled": False, "display_order": 14, "is_custom": True, "description": "Proof point: Receipt"},
        {"column_name": "pp_brand_name", "enabled": False, "display_order": 15, "is_custom": True, "description": "Proof point: Brand name"},
        {"column_name": "pp_dist_subcontractor", "enabled": True, "display_order": 16, "description": "Subcontractor name"},
        {"column_name": "pp_prod_purchase", "enabled": False, "display_order": 17, "is_custom": True, "description": "Proof point: Product purchase"},
        {"column_name": "tradenet_company_id", "enabled": True, "display_order": 18, "description": "TradeNet company ID"},
    ]

    columns = await ColumnSettingsRepository.bulk_upsert(db, default_columns)
    return columns
