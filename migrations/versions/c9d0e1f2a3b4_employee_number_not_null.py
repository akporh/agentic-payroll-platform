"""MIG-18-A: employee_number NOT NULL + workspace-scoped unique index

Revision ID: c9d0e1f2a3b4
Revises: f0a1b2c3d4e5
Create Date: 2026-05-31 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, Sequence[str], None] = "f0a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE employee ALTER COLUMN employee_number SET NOT NULL;
        EXCEPTION WHEN others THEN NULL; END $$;
    """)

    op.execute("DROP INDEX IF EXISTS uq_employee_number_per_workspace;")

    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_employee_number
            ON employee (workspace_id, employee_number);
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ux_employee_number;")

    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_employee_number_per_workspace
            ON employee (workspace_id, employee_number);
    """)

    op.execute("""
        ALTER TABLE employee ALTER COLUMN employee_number DROP NOT NULL;
    """)
