"""Activity logging model for tracking processing runs."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, ARRAY
from app.database import Base


class ActivityLog(Base):
    """Activity log for processing runs and operations."""

    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(100), nullable=False, unique=True, index=True)
    run_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = Column(String(50), nullable=False)  # success, error, warning, processing

    # Processing details
    input_files = Column(JSON, nullable=True)  # List of uploaded file names
    members_processed = Column(Integer, default=0)
    total_rows_processed = Column(Integer, default=0)
    total_rows_output = Column(Integer, default=0)

    # Warnings and errors
    warnings = Column(JSON, nullable=True)  # Array of warning messages
    errors = Column(JSON, nullable=True)  # Array of error messages

    # Performance metrics
    duration_seconds = Column(Integer, nullable=True)

    # Additional details
    details = Column(JSON, nullable=True)  # Additional metadata

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ActivityLog(run_id={self.run_id}, status={self.status})>"
