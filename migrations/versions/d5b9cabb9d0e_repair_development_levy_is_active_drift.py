"""Repair DEVELOPMENT_LEVY component_metadata.is_active data drift + dead-key cleanup.

Seed migration c1d2e3f4a5b6 set component_metadata.DEVELOPMENT_LEVY.is_active =
TRUE, but the dev/prod DB has since drifted to FALSE (manual flip), which
excludes the component from the execution graph entirely
(backend/api/routes/payroll.py's active-components query and
sequential_executor.py both filter is_active = TRUE). This is data repair,
not a schema or seed-value change — the guarded UPDATE only touches rows
that have actually drifted from seed truth.

Separately, client_component_metadata.overrides_json historically carried a
dead 'is_active' key that nothing reads (the dedicated is_active column,
added later, is authoritative). Before stripping that dead key, this
migration checks whether any row's overrides_json.is_active disagrees with
the dedicated column — a disagreement may be forensic evidence of a past
bug, not just dead data, so those rows are logged via RAISE NOTICE and
excluded from the delete rather than silently cleaned up.

Revision ID: d5b9cabb9d0e
Revises: b8c9d0e1f2a3
Create Date: 2026-07-16
"""
from alembic import op

revision = "d5b9cabb9d0e"
down_revision = "b8c9d0e1f2a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Step 1: repair the is_active drift (guarded, not a blind SET) ---
    op.execute("""
        DO $$
        DECLARE
            affected_count integer;
        BEGIN
            UPDATE component_metadata
            SET is_active = TRUE
            WHERE component_code = 'DEVELOPMENT_LEVY'
              AND country_code   = 'NG'
              AND is_active      = FALSE;

            GET DIAGNOSTICS affected_count = ROW_COUNT;
            RAISE NOTICE 'd5b9cabb9d0e: repaired is_active drift on % component_metadata row(s)', affected_count;
        END $$;
    """)

    # --- Step 2: dead-key cleanup, with a disagreement pre-check ---
    op.execute("""
        DO $$
        DECLARE
            disagreeing_count integer;
            cleaned_count      integer;
        BEGIN
            -- Log (not delete) rows where the dead key disagrees with the
            -- authoritative column — possible forensic evidence of a past bug.
            SELECT count(*) INTO disagreeing_count
            FROM client_component_metadata
            WHERE overrides_json ? 'is_active'
              AND (overrides_json ->> 'is_active')::boolean IS DISTINCT FROM is_active;

            IF disagreeing_count > 0 THEN
                RAISE NOTICE 'd5b9cabb9d0e: % client_component_metadata row(s) have overrides_json.is_active disagreeing with the is_active column — left untouched, not deleted', disagreeing_count;
            END IF;

            -- Only strip the dead key from rows where it agrees with (or the
            -- column has no material disagreement recorded above).
            UPDATE client_component_metadata
            SET overrides_json = overrides_json - 'is_active'
            WHERE overrides_json ? 'is_active'
              AND (overrides_json ->> 'is_active')::boolean IS NOT DISTINCT FROM is_active;

            GET DIAGNOSTICS cleaned_count = ROW_COUNT;
            RAISE NOTICE 'd5b9cabb9d0e: stripped dead overrides_json.is_active key from % row(s)', cleaned_count;
        END $$;
    """)


def downgrade() -> None:
    # No-op by design: seed truth for DEVELOPMENT_LEVY.is_active is TRUE
    # (c1d2e3f4a5b6). Downgrading to FALSE would just reintroduce the
    # original "levy never fires" bug this migration exists to fix.
    # The dead-key strip (step 2) is also not reversed — the key was
    # confirmed dead (nothing reads it) before being removed.
    pass
