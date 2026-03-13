"""add_salary_definition_code

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-03-10 00:01:00.000000

Adds a human-readable `code` column to salary_definition.
Code format: UPPER(designation)_UPPER(grade), e.g. ENGINEER_G5.

Backfill for existing rows uses UPPER(REPLACE(name, ' ', '_')) as a fallback
since designation/grade are not stored on the salary_definition table itself.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c2d3e4f5a6b7'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Add column as nullable so backfill can run first
    op.add_column(
        "salary_definition",
        sa.Column("code", sa.String(120), nullable=True),
    )

    # 2. Backfill: derive code from name (UPPER + spaces → underscores).
    #    Disable the immutability trigger temporarily — this is a schema-level
    #    migration adding a new column, not a business data change.
    op.execute("ALTER TABLE salary_definition DISABLE TRIGGER ALL")
    op.execute("""
        UPDATE salary_definition
        SET code = UPPER(REPLACE(COALESCE(name, 'UNKNOWN'), ' ', '_'))
        WHERE code IS NULL
    """)
    op.execute("ALTER TABLE salary_definition ENABLE TRIGGER ALL")

    # 3. Enforce NOT NULL now that all rows have a value
    op.alter_column("salary_definition", "code", nullable=False)

    # 4. Add unique constraint scoped per workspace
    op.create_index(
        "uq_salary_definition_code_workspace",
        "salary_definition",
        ["workspace_id", "code"],
        unique=True,
    )


def downgrade():
    op.drop_index("uq_salary_definition_code_workspace", table_name="salary_definition")
    op.drop_column("salary_definition", "code")
