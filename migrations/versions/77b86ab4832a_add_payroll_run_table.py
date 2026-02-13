"""add payroll_run table

Revision ID: 77b86ab4832a
Revises: 4758b5bfe177
Create Date: 2026-02-13 13:13:07.688811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77b86ab4832a'
down_revision: Union[str, Sequence[str], None] = '4758b5bfe177'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payroll_run",
        sa.Column("payroll_run_id", sa.UUID(), primary_key=True),
        sa.Column("workspace_id", sa.UUID(),
                  sa.ForeignKey("workspace.workspace_id"),
                  nullable=False),

        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("pay_date", sa.Date(), nullable=False),

        sa.Column("total_gross_pay", sa.Numeric(), nullable=True),
        sa.Column("total_deduction", sa.Numeric(), nullable=True),
        sa.Column("total_net_pay", sa.Numeric(), nullable=True),

        sa.Column("status", sa.String(), nullable=False),
    )



def downgrade() -> None:
    op.drop_table("payroll_run")

