"""MIG-18-D: Add public_holidays_snapshot JSONB column to payroll_run

Revision ID: e9f0a1b2c3d4
Revises: f0a1b2c3d4e5
Create Date: 2026-05-31 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op

revision: str = "e9f0a1b2c3d4"
down_revision: Union[str, Sequence[str], None] = "f0a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE payroll_run ADD COLUMN public_holidays_snapshot JSONB;
        EXCEPTION WHEN duplicate_column THEN NULL; END $$;
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE payroll_run DROP COLUMN IF EXISTS public_holidays_snapshot;")
