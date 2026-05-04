"""Add per_employee_context_json to payroll_result — Sprint 13 M3 D4/D5

Stores frozen employee eligibility flags (e.g. is_union_member) at result-write time
so that per-employee and full-run retries reproduce the original eligibility decision
rather than re-reading from the live employee_contract table.

Safe: trg_snapshot_immutable fires BEFORE UPDATE OF calculations_snapshot_json only —
column-specific. This new column is unaffected by the trigger.

Revision ID: 1a2b3c4d5e6f
Revises: 0a1b2c3d4e5f
Create Date: 2026-05-04 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = "1a2b3c4d5e6f"
down_revision: Union[str, Sequence[str], None] = "0a1b2c3d4e5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    DO $$ BEGIN
        ALTER TABLE payroll_result
        ADD COLUMN per_employee_context_json JSONB NULL;
    EXCEPTION WHEN duplicate_column THEN NULL;
    END $$;
    """)


def downgrade() -> None:
    op.execute("""
    ALTER TABLE payroll_result DROP COLUMN IF EXISTS per_employee_context_json;
    """)
