"""add salary_definition table

Revision ID: 94a312394013
Revises: 77c459d173ca
Create Date: 2026-02-14 04:53:44.433889

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94a312394013'
down_revision: Union[str, Sequence[str], None] = '77c459d173ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "salary_definition",
        sa.Column("salary_definition_id", sa.UUID(), primary_key=True),
        sa.Column("employee_id", sa.UUID(),
                  sa.ForeignKey("employee.employee_id"),
                  nullable=False),

        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),

        sa.Column("components_jsonb", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.func.now()),
    )

def downgrade() -> None:
    op.drop_table("salary_definition")

