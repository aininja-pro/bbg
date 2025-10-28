"""Settings model for user preferences and configuration."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from app.database import Base


class Settings(Base):
    """User settings and preferences."""

    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), nullable=False, unique=True, index=True)
    setting_value = Column(JSON, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Settings(key={self.setting_key})>"


class ColumnSettings(Base):
    """Column visibility and order settings."""

    __tablename__ = "column_settings"

    id = Column(Integer, primary_key=True, index=True)
    column_name = Column(String(100), nullable=False, unique=True, index=True)
    enabled = Column(Boolean, nullable=False, default=True)
    display_order = Column(Integer, nullable=False, default=0)
    is_custom = Column(Boolean, nullable=False, default=False)  # For new pp_ fields
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ColumnSettings(column={self.column_name}, enabled={self.enabled})>"
