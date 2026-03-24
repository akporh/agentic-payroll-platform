"""period_aware_input_linking_index

Adds a partial index on payroll_input(workspace_id, reference_date) to
accelerate period-scoped input linking queries introduced in the v2
period-aware payroll engine.

The index covers only unclaimed rows (payroll_run_id IS NULL) — these are
the rows scanned during link_inputs_to_run() and
load_unclaimed_inputs_by_employee().  Claimed rows are never queried by
those functions and are therefore excluded to keep the index small.

No schema column changes are made — reference_date already exists
(migration d3e4f5a6b7c8).

Revision ID: e2a3b4c5d6f7
Revises: d1a2b3c4d5e6
Create Date: 2026-03-23 00:00:00.000000
"""

from alembic import op

revision      = "e2a3b4c5d6f7"
down_revision = "d1a2b3c4d5e6"
branch_labels = None
depends_on    = None


def upgrade():
    op.execute("""
        CREATE INDEX idx_payroll_input_period_unclaimed
            ON payroll_input (workspace_id, reference_date)
         WHERE payroll_run_id IS NULL
    """)


def downgrade():
    op.execute(
        "DROP INDEX IF EXISTS idx_payroll_input_period_unclaimed"
    )
