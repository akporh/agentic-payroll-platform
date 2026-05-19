"""Add partial unique index on payroll_input for unclaimed rows

Revision ID: b2c3d4e5f6a8
Revises: a1b2c3d4e5f7
Create Date: 2026-04-08 00:01:00.000000

Prevents re-uploading the same (workspace_id, employee_id, input_code, reference_date)
combination when those inputs are unclaimed (not yet linked to a payroll run).
Once a run claims inputs (payroll_run_id IS NOT NULL), the constraint no longer
applies — the same codes can be re-uploaded for a future run.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "b2c3d4e5f6a8"
down_revision: Union[str, None] = "a1b2c3d4e5f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE UNIQUE INDEX uq_payroll_input_unclaimed
        ON payroll_input (workspace_id, employee_id, input_code, reference_date)
        WHERE payroll_run_id IS NULL
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_payroll_input_unclaimed")
