"""Add territory_manager to members

Revision ID: 004
Revises: 003
Create Date: 2025-11-22 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add territory_manager column to lookup_members
    op.add_column('lookup_members', sa.Column('territory_manager', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_lookup_members_territory_manager'), 'lookup_members', ['territory_manager'], unique=False)


def downgrade() -> None:
    # Remove territory_manager column and its index
    op.drop_index(op.f('ix_lookup_members_territory_manager'), table_name='lookup_members')
    op.drop_column('lookup_members', 'territory_manager')
