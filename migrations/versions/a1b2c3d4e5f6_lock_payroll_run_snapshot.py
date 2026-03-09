"""Lock payroll_run rules_context_snapshot after insert

Revision ID: a1b2c3d4e5f6
Revises: d5e6f7a8b9c0
Create Date: 2026-03-04

Makes payroll_run.rules_context_snapshot physically immutable via a
BEFORE UPDATE trigger.  Once the snapshot is written on INSERT it must
never change — the trigger raises an exception on any attempt to update
the column to a different value.

Modelled after trg_snapshot_immutable on payroll_result
(migration fe0bad282b7d).
"""

from typing import Sequence, Union

from alembic import op


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "d5e6f7a8b9c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE FUNCTION prevent_run_snapshot_update()
    RETURNS trigger AS $$
    BEGIN
        IF NEW.rules_context_snapshot IS DISTINCT FROM OLD.rules_context_snapshot THEN
            RAISE EXCEPTION 'rules_context_snapshot is immutable';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("DROP TRIGGER IF EXISTS trg_run_snapshot_immutable ON payroll_run;")

    op.execute("""
    CREATE TRIGGER trg_run_snapshot_immutable
    BEFORE UPDATE OF rules_context_snapshot ON payroll_run
    FOR EACH ROW
    WHEN (OLD.rules_context_snapshot IS DISTINCT FROM NEW.rules_context_snapshot)
    EXECUTE FUNCTION prevent_run_snapshot_update();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_run_snapshot_immutable ON payroll_run;")
    op.execute("DROP FUNCTION IF EXISTS prevent_run_snapshot_update();")
