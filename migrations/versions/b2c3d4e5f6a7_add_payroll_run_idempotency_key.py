"""Add idempotency_key to payroll_run

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-04

Adds database-level idempotency protection for payroll runs so that the
same API request (retried due to network failure, timeout, etc.) cannot
create duplicate payroll run records.

Changes
-------
1. New column: payroll_run.idempotency_key TEXT (nullable)
   Callers may supply any opaque string (UUID, request-id, etc.).
   NULL means "no idempotency key was provided" — allowed to be non-unique.

2. New partial unique index: ux_payroll_run_idempotency
   Enforces (workspace_id, idempotency_key) uniqueness ONLY when
   idempotency_key IS NOT NULL.  This prevents a retried request from
   inserting a second run for the same logical operation while leaving
   historical runs without keys unaffected.

Pay-period protection (already in place)
-----------------------------------------
A unique index preventing duplicate runs for the same pay period already
exists from migration 6f5b05ff4690:

    uq_payroll_run_period ON payroll_run(workspace_id, period_start, period_end)

No change is needed for that constraint; this migration only adds the
idempotency-key mechanism on top.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add the idempotency_key column (nullable — existing rows get NULL)
    op.execute("""
        ALTER TABLE payroll_run
        ADD COLUMN IF NOT EXISTS idempotency_key TEXT;
    """)

    # 2. Partial unique index — only enforced when a key is present
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_payroll_run_idempotency
        ON payroll_run(workspace_id, idempotency_key)
        WHERE idempotency_key IS NOT NULL;
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ux_payroll_run_idempotency;")
    op.execute("ALTER TABLE payroll_run DROP COLUMN IF EXISTS idempotency_key;")
