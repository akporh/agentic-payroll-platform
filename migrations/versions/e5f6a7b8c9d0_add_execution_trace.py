"""add_execution_trace

Revision ID: e5f6a7b8c9d0
Revises: c2d3e4f5a6b7
Create Date: 2026-03-11 00:00:00.000000

Adds execution_trace table to persist structured step-level traces
produced by ExecutionTracer during a payroll run.

No foreign key to payroll_run because trace steps are written during
execution, before the payroll_run row is committed.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'c2d3e4f5a6b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'execution_trace',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('run_id', UUID(as_uuid=True), nullable=False),
        sa.Column('step_name', sa.String(200), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),   # 'success' | 'error'
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('ix_execution_trace_run_id', 'execution_trace', ['run_id'])


def downgrade():
    op.drop_index('ix_execution_trace_run_id', table_name='execution_trace')
    op.drop_table('execution_trace')
