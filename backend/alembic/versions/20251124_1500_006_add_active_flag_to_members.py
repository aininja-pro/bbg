"""Add active_flag to members

Revision ID: 006
Revises: 005
Create Date: 2025-11-24 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add active_flag column to lookup_members
    op.add_column('lookup_members', sa.Column('active_flag', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove active_flag column
    op.drop_column('lookup_members', 'active_flag')
