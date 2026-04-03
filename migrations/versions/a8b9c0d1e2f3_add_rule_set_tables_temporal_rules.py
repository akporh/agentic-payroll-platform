"""Add rule_set tables and temporal rule columns.

Introduces versioned, immutable rule sets per workspace:

  rule_set       — one row per published rule set; write-once, never updated.
  rule_set_item  — rule content within a rule set; write-once, never updated.

Adds temporal columns to existing tables:

  statutory_rule.effective_from         — date-based statutory rule selection.
  payroll_run.rule_set_id               — FK to the rule set used for this run.
  payroll_run.statutory_effective_date  — date used to select the statutory rule.
  payroll_run.run_type                  — REGULAR or ADJUSTMENT.

Constraint change on payroll_run:
  DROP   uq_payroll_run_period        (unique per workspace+period, all runs)
  CREATE uq_payroll_run_regular       (unique per workspace+period, REGULAR only)

This allows multiple ADJUSTMENT runs for the same period while still
preventing duplicate REGULAR runs.

Revision ID: a8b9c0d1e2f3
Revises: f3a4b5c6d7e8
Create Date: 2026-03-25
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a8b9c0d1e2f3"
down_revision: Union[str, Sequence[str], None] = "f3a4b5c6d7e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. rule_set ───────────────────────────────────────────────────────────
    # Immutable once created. No UNIQUE on (workspace_id, effective_from) so
    # that corrections can be published with the same effective date as an
    # existing rule set; the selection query uses created_at as a tiebreaker.
    op.execute("""
        CREATE TABLE rule_set (
            rule_set_id    UUID         NOT NULL DEFAULT gen_random_uuid(),
            workspace_id   UUID         NOT NULL,
            effective_from DATE         NOT NULL,
            created_at     TIMESTAMPTZ  NOT NULL DEFAULT now(),
            created_by     UUID         NOT NULL,

            CONSTRAINT pk_rule_set PRIMARY KEY (rule_set_id),
            CONSTRAINT fk_rule_set_workspace
                FOREIGN KEY (workspace_id)
                REFERENCES workspace (workspace_id)
        );
    """)

    op.execute("""
        CREATE INDEX idx_rule_set_workspace_effective
            ON rule_set (workspace_id, effective_from DESC, created_at DESC);
    """)

    # ── 2. rule_set_item ──────────────────────────────────────────────────────
    # Content is copied at publish time and never modified.
    op.execute("""
        CREATE TABLE rule_set_item (
            rule_set_id          UUID  NOT NULL,
            rule_name            TEXT  NOT NULL,
            rule_definition_json JSONB NOT NULL,
            rule_type            TEXT,

            CONSTRAINT pk_rule_set_item PRIMARY KEY (rule_set_id, rule_name),
            CONSTRAINT fk_rule_set_item_rule_set
                FOREIGN KEY (rule_set_id)
                REFERENCES rule_set (rule_set_id)
        );
    """)

    # ── 3. statutory_rule.effective_from ─────────────────────────────────────
    # Backfill existing rows with 2000-01-01 so they are always selected when
    # as_of_date >= 2000-01-01 (i.e., always).
    op.execute("""
        ALTER TABLE statutory_rule
            ADD COLUMN IF NOT EXISTS effective_from DATE NOT NULL DEFAULT '2000-01-01';
    """)

    # ── 4. payroll_run — new temporal columns ─────────────────────────────────
    op.execute("""
        ALTER TABLE payroll_run
            ADD COLUMN IF NOT EXISTS rule_set_id             UUID
                REFERENCES rule_set (rule_set_id),
            ADD COLUMN IF NOT EXISTS statutory_effective_date DATE,
            ADD COLUMN IF NOT EXISTS run_type                TEXT NOT NULL DEFAULT 'REGULAR';
    """)

    # ── 5. Replace the all-runs period uniqueness constraint ─────────────────
    # Old index: unique per (workspace_id, period_start, period_end) for ALL runs.
    # New index: unique per (workspace_id, period_start, period_end) for REGULAR only.
    op.execute("""
        DROP INDEX IF EXISTS uq_payroll_run_period;
    """)

    op.execute("""
        CREATE UNIQUE INDEX uq_payroll_run_regular
            ON payroll_run (workspace_id, period_start, period_end)
            WHERE run_type = 'REGULAR';
    """)


def downgrade() -> None:
    # Restore the original all-runs uniqueness constraint
    op.execute("DROP INDEX IF EXISTS uq_payroll_run_regular;")

    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_payroll_run_period
            ON payroll_run (workspace_id, period_start, period_end);
    """)

    op.execute("""
        ALTER TABLE payroll_run
            DROP COLUMN IF EXISTS run_type,
            DROP COLUMN IF EXISTS statutory_effective_date,
            DROP COLUMN IF EXISTS rule_set_id;
    """)

    op.execute("""
        ALTER TABLE statutory_rule
            DROP COLUMN IF EXISTS effective_from;
    """)

    op.execute("DROP TABLE IF EXISTS rule_set_item;")
    op.execute("DROP TABLE IF EXISTS rule_set;")
