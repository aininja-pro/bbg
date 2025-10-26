"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2025-01-19 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create lookup_members table
    op.create_table(
        'lookup_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tradenet_company_id', sa.String(length=100), nullable=False),
        sa.Column('bbg_member_id', sa.String(length=100), nullable=True),
        sa.Column('member_name', sa.String(length=255), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lookup_members_bbg_member_id'), 'lookup_members', ['bbg_member_id'], unique=False)
    op.create_index(op.f('ix_lookup_members_id'), 'lookup_members', ['id'], unique=False)
    op.create_index(op.f('ix_lookup_members_tradenet_company_id'), 'lookup_members', ['tradenet_company_id'], unique=False)
    op.create_index(op.f('ix_lookup_members_member_name'), 'lookup_members', ['member_name'], unique=False)

    # Create lookup_suppliers table
    op.create_table(
        'lookup_suppliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tradenet_supplier_id', sa.String(length=100), nullable=False),
        sa.Column('supplier_name', sa.String(length=255), nullable=False),
        sa.Column('contact_info', sa.Text(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tradenet_supplier_id')
    )
    op.create_index(op.f('ix_lookup_suppliers_id'), 'lookup_suppliers', ['id'], unique=False)
    op.create_index(op.f('ix_lookup_suppliers_tradenet_supplier_id'), 'lookup_suppliers', ['tradenet_supplier_id'], unique=True)
    op.create_index(op.f('ix_lookup_suppliers_supplier_name'), 'lookup_suppliers', ['supplier_name'], unique=False)

    # Create lookup_products table
    op.create_table(
        'lookup_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('program_id', sa.String(length=100), nullable=False),
        sa.Column('program_name', sa.String(length=255), nullable=False),
        sa.Column('product_id', sa.String(length=100), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('proof_point', sa.String(length=255), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lookup_products_id'), 'lookup_products', ['id'], unique=False)
    op.create_index(op.f('ix_lookup_products_product_id'), 'lookup_products', ['product_id'], unique=False)
    op.create_index(op.f('ix_lookup_products_program_id'), 'lookup_products', ['program_id'], unique=False)

    # Create rules table
    op.create_table(
        'rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('config', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rules_id'), 'rules', ['id'], unique=False)
    op.create_index(op.f('ix_rules_priority'), 'rules', ['priority'], unique=False)

    # Create activity_logs table
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_id', sa.String(length=100), nullable=False),
        sa.Column('run_timestamp', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('input_files', sa.JSON(), nullable=True),
        sa.Column('members_processed', sa.Integer(), nullable=True),
        sa.Column('total_rows_processed', sa.Integer(), nullable=True),
        sa.Column('total_rows_output', sa.Integer(), nullable=True),
        sa.Column('warnings', sa.JSON(), nullable=True),
        sa.Column('errors', sa.JSON(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('run_id')
    )
    op.create_index(op.f('ix_activity_logs_id'), 'activity_logs', ['id'], unique=False)
    op.create_index(op.f('ix_activity_logs_run_id'), 'activity_logs', ['run_id'], unique=True)
    op.create_index(op.f('ix_activity_logs_run_timestamp'), 'activity_logs', ['run_timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_activity_logs_run_timestamp'), table_name='activity_logs')
    op.drop_index(op.f('ix_activity_logs_run_id'), table_name='activity_logs')
    op.drop_index(op.f('ix_activity_logs_id'), table_name='activity_logs')
    op.drop_table('activity_logs')

    op.drop_index(op.f('ix_rules_priority'), table_name='rules')
    op.drop_index(op.f('ix_rules_id'), table_name='rules')
    op.drop_table('rules')

    op.drop_index(op.f('ix_lookup_products_program_id'), table_name='lookup_products')
    op.drop_index(op.f('ix_lookup_products_product_id'), table_name='lookup_products')
    op.drop_index(op.f('ix_lookup_products_id'), table_name='lookup_products')
    op.drop_table('lookup_products')

    op.drop_index(op.f('ix_lookup_suppliers_tradenet_supplier_id'), table_name='lookup_suppliers')
    op.drop_index(op.f('ix_lookup_suppliers_id'), table_name='lookup_suppliers')
    op.drop_table('lookup_suppliers')

    op.drop_index(op.f('ix_lookup_members_tradenet_company_id'), table_name='lookup_members')
    op.drop_index(op.f('ix_lookup_members_bbg_member_id'), table_name='lookup_members')
    op.drop_index(op.f('ix_lookup_members_id'), table_name='lookup_members')
    op.drop_table('lookup_members')
