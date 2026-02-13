"""add payroll_result table

Revision ID: 45ad7410d53e
Revises: 77b86ab4832a
Create Date: 2026-02-13 13:15:35.110251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45ad7410d53e'
down_revision: Union[str, Sequence[str], None] = '77b86ab4832a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payroll_result",
        sa.Column("payroll_result_id", sa.UUID(), primary_key=True),

        sa.Column("payroll_run_id", sa.UUID(),
                  sa.ForeignKey("payroll_run.payroll_run_id"),
                  nullable=False),

        sa.Column("employee_id", sa.UUID(),
                  sa.ForeignKey("employee.employee_id"),
                  nullable=False),

        sa.Column("gross_components_jsonb", sa.JSON(), nullable=True),
        sa.Column("deductions_jsonb", sa.JSON(), nullable=True),

        sa.Column("net_pay", sa.Numeric(), nullable=False),

        sa.Column("calculations_snapshot_json", sa.JSON(), nullable=False),

        sa.Column("generated_at", sa.TIMESTAMP(), server_default=sa.func.now()),
    )



def downgrade() -> None:
    op.drop_table("payroll_result")

