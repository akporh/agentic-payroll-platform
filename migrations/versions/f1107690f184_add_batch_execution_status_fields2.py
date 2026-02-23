"""add batch execution status fields

Revision ID: f1107690f184
Revises: 8c3b7a7eb23a
Create Date: 2026-02-21 18:07:05.938626

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1107690f184'
down_revision: Union[str, Sequence[str], None] = '8c3b7a7eb23a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add status + error_message to payroll_result
    op.add_column(
        "payroll_result",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="SUCCESS",
        ),
    )

    op.add_column(
        "payroll_result",
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),
    )

    # Optional: remove server_default after backfill
    op.alter_column(
        "payroll_result",
        "status",
        server_default=None,
    )


def downgrade():
    op.drop_column("payroll_result", "error_message")
    op.drop_column("payroll_result", "status")