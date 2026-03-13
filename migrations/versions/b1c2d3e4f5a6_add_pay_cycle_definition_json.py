"""add_pay_cycle_definition_json

Revision ID: b1c2d3e4f5a6
Revises: a1c2e3f4b5d6
Create Date: 2026-03-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = 'a1c2e3f4b5d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "pay_cycle",
        sa.Column("definition_json", postgresql.JSONB, nullable=True),
    )


def downgrade():
    op.drop_column("pay_cycle", "definition_json")
