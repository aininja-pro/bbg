"""Repository for settings database operations."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.settings import Settings, ColumnSettings
from app.schemas.settings import (
    SettingsCreate,
    SettingsUpdate,
    ColumnSettingsCreate,
    ColumnSettingsUpdate,
)


class SettingsRepository:
    """Repository for settings CRUD operations."""

    @staticmethod
    async def get_by_key(db: AsyncSession, setting_key: str) -> Optional[Settings]:
        """Get setting by key."""
        result = await db.execute(
            select(Settings).where(Settings.setting_key == setting_key)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Settings]:
        """Get all settings."""
        result = await db.execute(select(Settings))
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, setting: SettingsCreate) -> Settings:
        """Create new setting."""
        db_setting = Settings(**setting.model_dump())
        db.add(db_setting)
        await db.commit()
        await db.refresh(db_setting)
        return db_setting

    @staticmethod
    async def update(
        db: AsyncSession, setting_key: str, setting: SettingsUpdate
    ) -> Optional[Settings]:
        """Update existing setting."""
        db_setting = await SettingsRepository.get_by_key(db, setting_key)
        if not db_setting:
            return None

        for key, value in setting.model_dump(exclude_unset=True).items():
            setattr(db_setting, key, value)

        await db.commit()
        await db.refresh(db_setting)
        return db_setting

    @staticmethod
    async def upsert(
        db: AsyncSession, setting_key: str, setting_value: dict, description: str = None
    ) -> Settings:
        """Create or update setting."""
        db_setting = await SettingsRepository.get_by_key(db, setting_key)

        if db_setting:
            db_setting.setting_value = setting_value
            if description:
                db_setting.description = description
        else:
            db_setting = Settings(
                setting_key=setting_key,
                setting_value=setting_value,
                description=description,
            )
            db.add(db_setting)

        await db.commit()
        await db.refresh(db_setting)
        return db_setting


class ColumnSettingsRepository:
    """Repository for column settings CRUD operations."""

    @staticmethod
    async def get_by_name(
        db: AsyncSession, column_name: str
    ) -> Optional[ColumnSettings]:
        """Get column setting by name."""
        result = await db.execute(
            select(ColumnSettings).where(ColumnSettings.column_name == column_name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[ColumnSettings]:
        """Get all column settings ordered by display_order."""
        result = await db.execute(
            select(ColumnSettings).order_by(ColumnSettings.display_order)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_enabled(db: AsyncSession) -> List[ColumnSettings]:
        """Get all enabled column settings."""
        result = await db.execute(
            select(ColumnSettings)
            .where(ColumnSettings.enabled == True)
            .order_by(ColumnSettings.display_order)
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(
        db: AsyncSession, column_setting: ColumnSettingsCreate
    ) -> ColumnSettings:
        """Create new column setting."""
        db_column = ColumnSettings(**column_setting.model_dump())
        db.add(db_column)
        await db.commit()
        await db.refresh(db_column)
        return db_column

    @staticmethod
    async def update(
        db: AsyncSession, column_name: str, column_setting: ColumnSettingsUpdate
    ) -> Optional[ColumnSettings]:
        """Update existing column setting."""
        db_column = await ColumnSettingsRepository.get_by_name(db, column_name)
        if not db_column:
            return None

        for key, value in column_setting.model_dump(exclude_unset=True).items():
            setattr(db_column, key, value)

        await db.commit()
        await db.refresh(db_column)
        return db_column

    @staticmethod
    async def upsert(
        db: AsyncSession,
        column_name: str,
        enabled: bool = True,
        display_order: int = 0,
        is_custom: bool = False,
        description: str = None,
    ) -> ColumnSettings:
        """Create or update column setting."""
        db_column = await ColumnSettingsRepository.get_by_name(db, column_name)

        if db_column:
            db_column.enabled = enabled
            db_column.display_order = display_order
            if description:
                db_column.description = description
        else:
            db_column = ColumnSettings(
                column_name=column_name,
                enabled=enabled,
                display_order=display_order,
                is_custom=is_custom,
                description=description,
            )
            db.add(db_column)

        await db.commit()
        await db.refresh(db_column)
        return db_column

    @staticmethod
    async def bulk_upsert(db: AsyncSession, columns: List[dict]) -> List[ColumnSettings]:
        """Bulk create or update column settings."""
        # First, fetch ALL existing columns at once to avoid querying in loop
        existing_columns_list = await ColumnSettingsRepository.get_all(db)
        existing_map = {col.column_name: col for col in existing_columns_list}

        result = []

        for col_data in columns:
            column_name = col_data.get("column_name")
            enabled = col_data.get("enabled", True)
            display_order = col_data.get("display_order", 0)
            is_custom = col_data.get("is_custom", False)
            description = col_data.get("description")

            # Check if exists in pre-fetched map
            db_column = existing_map.get(column_name)

            if db_column:
                # Update existing
                db_column.enabled = enabled
                db_column.display_order = display_order
                if description:
                    db_column.description = description
            else:
                # Create new
                db_column = ColumnSettings(
                    column_name=column_name,
                    enabled=enabled,
                    display_order=display_order,
                    is_custom=is_custom,
                    description=description,
                )
                db.add(db_column)
                existing_map[column_name] = db_column  # Add to map to prevent duplicates

            result.append(db_column)

        # Single commit at the end for all changes
        await db.commit()

        # Refresh all objects
        for col in result:
            await db.refresh(col)

        return result

    @staticmethod
    async def delete(db: AsyncSession, column_name: str) -> bool:
        """Delete column setting."""
        db_column = await ColumnSettingsRepository.get_by_name(db, column_name)
        if not db_column:
            return False

        await db.delete(db_column)
        await db.commit()
        return True
