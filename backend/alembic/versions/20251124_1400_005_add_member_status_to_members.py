"""Add member_status to members

Revision ID: 005
Revises: 004
Create Date: 2025-11-24 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add member_status column to lookup_members
    op.add_column('lookup_members', sa.Column('member_status', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Remove member_status column
    op.drop_column('lookup_members', 'member_status')
