"""Processed file storage model for caching processing results."""
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from app.database import Base


class ProcessedFile(Base):
    """Store processed CSV results for fast downloads without reprocessing."""

    __tablename__ = "processed_files"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), nullable=False, unique=True, index=True)

    # File information
    filename = Column(String(500), nullable=False)
    original_filenames = Column(JSON, nullable=True)  # Array of filenames for batch jobs
    file_type = Column(String(50), nullable=False)  # 'single', 'batch_merged', 'batch_zip'

    # Processing status
    status = Column(String(50), nullable=False, index=True)  # 'processing', 'completed', 'failed'

    # Processed data storage
    processed_data = Column(Text, nullable=True)  # CSV content as text (for single/merged)
    # For ZIP files, we'll store as base64 encoded text

    # Metadata
    total_rows = Column(Integer, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    processing_time_seconds = Column(Integer, nullable=True)
    processing_metadata = Column(JSON, nullable=True)  # Additional processing info (renamed from 'metadata' to avoid SQLAlchemy conflict)

    # Error handling
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)  # Auto-delete after 24 hours
    last_downloaded_at = Column(DateTime, nullable=True)
    download_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<ProcessedFile(job_id={self.job_id}, status={self.status}, filename={self.filename})>"

    @staticmethod
    def calculate_expiration(hours: int = 24) -> datetime:
        """Calculate expiration timestamp (default 24 hours from now)."""
        return datetime.utcnow() + timedelta(hours=hours)
