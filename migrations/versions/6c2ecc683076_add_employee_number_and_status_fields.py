"""add employee_number and status fields

Revision ID: 6c2ecc683076
Revises: 5ce90b326db6
Create Date: 2026-02-17 21:38:45.885198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c2ecc683076'
down_revision: Union[str, Sequence[str], None] = '5ce90b326db6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "employee",
        sa.Column("employee_number", sa.String(length=50), nullable=True),
    )

    op.add_column(
        "employee",
        sa.Column("status", sa.String(length=20), nullable=True),
    )

    op.add_column(
        "employee",
        sa.Column("personal_details_encrypted", sa.JSON(), nullable=True),
    )


def downgrade() -> None:

    op.drop_column("employee", "personal_details_encrypted")
    op.drop_column("employee", "status")
    op.drop_column("employee", "employee_number")
