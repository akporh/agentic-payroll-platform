"""add source column to uq_payroll_input_unclaimed partial index

Revision ID: ee5ff6aa7bb8
Revises: dd4ee5ff6aa7
Create Date: 2026-05-13
"""
from typing import Union, Sequence
from alembic import op
from sqlalchemy import text

revision: str = "ee5ff6aa7bb8"
down_revision: Union[str, Sequence[str], None] = "dd4ee5ff6aa7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    connection.execute(text("DROP INDEX IF EXISTS uq_payroll_input_unclaimed"))
    connection.execute(text("""
        CREATE UNIQUE INDEX uq_payroll_input_unclaimed
        ON payroll_input (workspace_id, employee_id, input_code, reference_date, source)
        WHERE payroll_run_id IS NULL
    """))


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(text("DROP INDEX IF EXISTS uq_payroll_input_unclaimed"))
    connection.execute(text("""
        CREATE UNIQUE INDEX uq_payroll_input_unclaimed
        ON payroll_input (workspace_id, employee_id, input_code, reference_date)
        WHERE payroll_run_id IS NULL
    """))
