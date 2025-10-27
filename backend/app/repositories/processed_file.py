"""Repository for ProcessedFile database operations."""
from datetime import datetime
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.processed_file import ProcessedFile
from app.schemas.processed_file import ProcessedFileCreate


class ProcessedFileRepository:
    """Repository for managing processed file storage."""

    @staticmethod
    async def create(db: AsyncSession, file_data: ProcessedFileCreate) -> ProcessedFile:
        """Create a new processed file record."""
        processed_file = ProcessedFile(**file_data.model_dump())
        db.add(processed_file)
        await db.commit()
        await db.refresh(processed_file)
        return processed_file

    @staticmethod
    async def get_by_job_id(db: AsyncSession, job_id: str) -> Optional[ProcessedFile]:
        """Get processed file by job_id."""
        result = await db.execute(
            select(ProcessedFile).where(ProcessedFile.job_id == job_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_status(
        db: AsyncSession,
        job_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> Optional[ProcessedFile]:
        """Update the status of a processed file."""
        processed_file = await ProcessedFileRepository.get_by_job_id(db, job_id)
        if processed_file:
            processed_file.status = status
            if error_message:
                processed_file.error_message = error_message
            await db.commit()
            await db.refresh(processed_file)
        return processed_file

    @staticmethod
    async def update_processed_data(
        db: AsyncSession,
        job_id: str,
        processed_data: str,
        total_rows: int,
        file_size_bytes: int,
        processing_time_seconds: int,
        processing_metadata: Optional[dict] = None
    ) -> Optional[ProcessedFile]:
        """Update processed file with the completed data."""
        processed_file = await ProcessedFileRepository.get_by_job_id(db, job_id)
        if processed_file:
            processed_file.processed_data = processed_data
            processed_file.total_rows = total_rows
            processed_file.file_size_bytes = file_size_bytes
            processed_file.processing_time_seconds = processing_time_seconds
            processed_file.status = 'completed'
            if processing_metadata:
                processed_file.processing_metadata = processing_metadata
            await db.commit()
            await db.refresh(processed_file)
        return processed_file

    @staticmethod
    async def record_download(db: AsyncSession, job_id: str) -> Optional[ProcessedFile]:
        """Record that a file was downloaded (update count and timestamp)."""
        processed_file = await ProcessedFileRepository.get_by_job_id(db, job_id)
        if processed_file:
            processed_file.download_count = (processed_file.download_count or 0) + 1
            processed_file.last_downloaded_at = datetime.utcnow()
            await db.commit()
            await db.refresh(processed_file)
        return processed_file

    @staticmethod
    async def delete_expired(db: AsyncSession) -> int:
        """Delete all expired processed files."""
        result = await db.execute(
            delete(ProcessedFile).where(ProcessedFile.expires_at < datetime.utcnow())
        )
        await db.commit()
        return result.rowcount

    @staticmethod
    async def delete_by_job_id(db: AsyncSession, job_id: str) -> bool:
        """Delete a specific processed file by job_id."""
        result = await db.execute(
            delete(ProcessedFile).where(ProcessedFile.job_id == job_id)
        )
        await db.commit()
        return result.rowcount > 0
