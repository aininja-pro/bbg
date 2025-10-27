"""Add bbg_id and active_flag to suppliers

Revision ID: 002
Revises: 001
Create Date: 2025-10-27 12:00:00.000000

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
    # Add bbg_id column to lookup_suppliers
    op.add_column('lookup_suppliers', sa.Column('bbg_id', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_lookup_suppliers_bbg_id'), 'lookup_suppliers', ['bbg_id'], unique=False)

    # Add active_flag column to lookup_suppliers
    op.add_column('lookup_suppliers', sa.Column('active_flag', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove active_flag column
    op.drop_column('lookup_suppliers', 'active_flag')

    # Remove bbg_id column and its index
    op.drop_index(op.f('ix_lookup_suppliers_bbg_id'), table_name='lookup_suppliers')
    op.drop_column('lookup_suppliers', 'bbg_id')
