"""Add composite index on salary_definition for effective date filtering

Revision ID: c3d4e5f6a7b9
Revises: b2c3d4e5f6a8
Create Date: 2026-04-08 00:02:00.000000

Supports the salary_definition effective date filter added to the payroll run
query. Without this index, each run would perform a full table scan on
salary_definition for every workspace when applying date bounds.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "c3d4e5f6a7b9"
down_revision: Union[str, None] = "b2c3d4e5f6a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_salary_definition_dates",
        "salary_definition",
        ["workspace_id", "effective_from", "effective_to"],
    )


def downgrade() -> None:
    op.drop_index("ix_salary_definition_dates", table_name="salary_definition")
