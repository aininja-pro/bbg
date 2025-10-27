"""Add processed_files table for caching results

Revision ID: 003
Revises: 002
Create Date: 2025-10-27 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create processed_files table
    op.create_table(
        'processed_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.String(length=100), nullable=False),
        sa.Column('filename', sa.String(length=500), nullable=False),
        sa.Column('original_filenames', sa.JSON(), nullable=True),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('processed_data', sa.Text(), nullable=True),
        sa.Column('total_rows', sa.Integer(), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('processing_time_seconds', sa.Integer(), nullable=True),
        sa.Column('processing_metadata', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('last_downloaded_at', sa.DateTime(), nullable=True),
        sa.Column('download_count', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id')
    )

    # Create indexes for performance
    op.create_index(op.f('ix_processed_files_id'), 'processed_files', ['id'], unique=False)
    op.create_index(op.f('ix_processed_files_job_id'), 'processed_files', ['job_id'], unique=True)
    op.create_index(op.f('ix_processed_files_status'), 'processed_files', ['status'], unique=False)
    op.create_index(op.f('ix_processed_files_created_at'), 'processed_files', ['created_at'], unique=False)
    op.create_index(op.f('ix_processed_files_expires_at'), 'processed_files', ['expires_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_processed_files_expires_at'), table_name='processed_files')
    op.drop_index(op.f('ix_processed_files_created_at'), table_name='processed_files')
    op.drop_index(op.f('ix_processed_files_status'), table_name='processed_files')
    op.drop_index(op.f('ix_processed_files_job_id'), table_name='processed_files')
    op.drop_index(op.f('ix_processed_files_id'), table_name='processed_files')

    # Drop table
    op.drop_table('processed_files')
