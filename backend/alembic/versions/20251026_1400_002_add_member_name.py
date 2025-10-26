"""Add member_name field to lookup_members

Revision ID: 002
Revises: 001
Create Date: 2025-10-26 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make bbg_member_id nullable (some members don't have it)
    op.alter_column('lookup_members', 'bbg_member_id',
                    existing_type=sa.String(length=100),
                    nullable=True)

    # Add member_name field with index for lookups
    op.add_column('lookup_members', sa.Column('member_name', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_lookup_members_member_name'), 'lookup_members', ['member_name'], unique=False)

    # Backfill existing data: copy member_name from member_name if it exists
    # (This handles the seed data that already exists)


def downgrade() -> None:
    # Remove the new field and index
    op.drop_index(op.f('ix_lookup_members_member_name'), table_name='lookup_members')
    op.drop_column('lookup_members', 'member_name')

    # Revert bbg_member_id to non-nullable
    op.alter_column('lookup_members', 'bbg_member_id',
                    existing_type=sa.String(length=100),
                    nullable=False)
