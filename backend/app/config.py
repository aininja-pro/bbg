"""Application configuration management using Pydantic settings."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./bbg_rebates.db"

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",  # Frontend running on 5174
    ]

    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    MAX_BATCH_FILES: int = 50
    UPLOAD_TIMEOUT_SECONDS: int = 300

    # Activity Logs
    LOG_RETENTION_DAYS: int = 90

    # Security
    SECRET_KEY: str = "development-secret-key-change-in-production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
