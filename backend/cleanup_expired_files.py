#!/usr/bin/env python3
"""
Cleanup script for expired processed files.

This script should be run periodically (e.g., via cron job) to delete
expired processed files from the database and free up storage.

Usage:
    python cleanup_expired_files.py

Cron example (run daily at 2 AM):
    0 2 * * * cd /path/to/BBG/backend && python cleanup_expired_files.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.repositories.processed_file import ProcessedFileRepository


async def cleanup_expired():
    """Delete all expired processed files from the database."""
    async with SessionLocal() as db:
        try:
            deleted_count = await ProcessedFileRepository.delete_expired(db)
            print(f"Successfully deleted {deleted_count} expired files")
            return deleted_count
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
            raise


if __name__ == "__main__":
    try:
        result = asyncio.run(cleanup_expired())
        sys.exit(0)
    except Exception as e:
        print(f"Cleanup failed: {str(e)}")
        sys.exit(1)
