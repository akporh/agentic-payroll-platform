"""add_payroll_input_table

Revision ID: d3e4f5a6b7c8
Revises: a7b8c9d0e1f2
Create Date: 2026-03-12 00:00:00.000000

Adds the payroll_input table as the canonical per-period event input layer.
Rows start unclaimed (payroll_run_id IS NULL) and are claimed during a
payroll run via UPDATE ... SET payroll_run_id = :run_id.

Changes
-------
1. Create payroll_input table with all input columns.
2. Add three FKs: employee, workspace, payroll_run.
3. Add three indexes for efficient lookup.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


revision: str = 'd3e4f5a6b7c8'
down_revision: Union[str, Sequence[str], None] = 'a7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'payroll_input',
        sa.Column(
            'payroll_input_id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
        ),
        sa.Column('workspace_id', UUID(as_uuid=True), nullable=False),
        sa.Column('payroll_run_id', UUID(as_uuid=True), nullable=True),
        sa.Column('employee_id', UUID(as_uuid=True), nullable=False),
        sa.Column('input_code', sa.String(50), nullable=False),
        sa.Column('input_category', sa.String(30), nullable=False),
        sa.Column('quantity', sa.Numeric(12, 2), nullable=True),
        sa.Column('rate', sa.Numeric(12, 2), nullable=True),
        sa.Column('amount', sa.Numeric(12, 2), nullable=True),
        sa.Column('reference_date', sa.Date(), nullable=True),
        sa.Column('source', sa.String(50), server_default='MANUAL'),
        sa.Column('input_json', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(
            ['employee_id'],
            ['employee.employee_id'],
            name='fk_input_employee',
        ),
        sa.ForeignKeyConstraint(
            ['workspace_id'],
            ['workspace.workspace_id'],
            name='fk_input_workspace',
        ),
        sa.ForeignKeyConstraint(
            ['payroll_run_id'],
            ['payroll_run.payroll_run_id'],
            name='fk_input_run',
        ),
        sa.CheckConstraint(
            "input_json IS NULL OR jsonb_typeof(input_json) = 'object'",
            name='ck_payroll_input_json_object',
        ),
    )

    op.create_index(
        'idx_payroll_input_employee',
        'payroll_input',
        ['employee_id'],
    )
    op.create_index(
        'idx_payroll_input_run',
        'payroll_input',
        ['payroll_run_id'],
    )
    op.create_index(
        'idx_payroll_input_code',
        'payroll_input',
        ['input_code'],
    )


def downgrade():
    op.drop_index('idx_payroll_input_code', table_name='payroll_input')
    op.drop_index('idx_payroll_input_run', table_name='payroll_input')
    op.drop_index('idx_payroll_input_employee', table_name='payroll_input')
    op.drop_table('payroll_input')
