"""add timesheet_entry table with derivation_status enum and policy_snapshot_jsonb

Revision ID: cc3dd4ee5ff6
Revises: bb2cc3dd4ee5
Create Date: 2026-05-13
"""
from typing import Union, Sequence
from alembic import op

revision: str = "cc3dd4ee5ff6"
down_revision: Union[str, Sequence[str], None] = "bb2cc3dd4ee5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE derivation_status AS ENUM ('PENDING', 'DERIVED', 'APPROVED', 'FAILED');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS timesheet_entry (
            timesheet_entry_id       UUID               PRIMARY KEY DEFAULT gen_random_uuid(),
            workspace_id             UUID               NOT NULL REFERENCES workspace(workspace_id),
            employee_id              UUID               NOT NULL REFERENCES employee(employee_id),
            period_start             DATE               NOT NULL,
            period_end               DATE               NOT NULL,
            attendance_grid_jsonb    JSONB              NOT NULL,
            derivation_status        derivation_status  NOT NULL DEFAULT 'PENDING',
            derivation_error         TEXT,
            policy_snapshot_jsonb    JSONB,
            derivation_summary_jsonb JSONB,
            created_at               TIMESTAMPTZ        NOT NULL DEFAULT now(),
            updated_at               TIMESTAMPTZ        NOT NULL DEFAULT now(),
            UNIQUE (workspace_id, employee_id, period_start)
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_timesheet_entry_workspace_period
        ON timesheet_entry (workspace_id, period_start)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_timesheet_entry_workspace_period")
    op.execute("DROP TABLE IF EXISTS timesheet_entry")
    op.execute("""
        DO $$ BEGIN
            DROP TYPE derivation_status;
        EXCEPTION WHEN undefined_object THEN NULL;
        END $$
    """)
