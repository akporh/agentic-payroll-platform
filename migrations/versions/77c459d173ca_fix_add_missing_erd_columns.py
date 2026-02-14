"""fix: add missing ERD columns

Revision ID: 77c459d173ca
Revises: 45ad7410d53e
Create Date: 2026-02-14 04:47:00.124453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77c459d173ca'
down_revision: Union[str, Sequence[str], None] = '45ad7410d53e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PAYROLL_RUN: add rules context snapshot
    op.add_column(
        "payroll_run",
        sa.Column("rules_context_snapshot", sa.JSON(), nullable=True),
    )

    # STATUTORY_RULE: add version number
    op.add_column(
        "statutory_rule",
        sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"),
    )

    # TAX_BAND: add effective dating
    op.add_column(
        "tax_band",
        sa.Column("effective_from", sa.Date(), nullable=True),
    )
    op.add_column(
        "tax_band",
        sa.Column("effective_to", sa.Date(), nullable=True),
    )

def downgrade() -> None:
    op.drop_column("tax_band", "effective_to")
    op.drop_column("tax_band", "effective_from")
    op.drop_column("statutory_rule", "version_number")
    op.drop_column("payroll_run", "rules_context_snapshot")

