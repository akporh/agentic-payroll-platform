"""Enforce payroll_run status transitions at the database level

Revision ID: f1a2b3c4d5e6
Revises: e2f3a4b5c6d7
Create Date: 2026-03-06

Replaces the legacy state-machine trigger (migration 9901bc4ed0c5, which used
obsolete PROCESSING/COMPLETED/FAILED/CANCELLED status values that no longer
exist in the codebase) with a correct implementation that mirrors the
application-level state machine and adds enforcement for INSERT.

Lifecycle enforced
------------------
The canonical forward lifecycle is:

    DRAFT → VALIDATED → CALCULATED → APPROVED → PAID

Intermediate statuses used by the calculation engine are mapped to lifecycle
ranks so that existing DB transitions remain valid without skipping rank
checks:

    ┌────────────┬──────┬─────────────────────────────────────────────────┐
    │ Status     │ Rank │ Notes                                           │
    ├────────────┼──────┼─────────────────────────────────────────────────┤
    │ DRAFT      │  1   │ Initial state; INSERT must use this status.     │
    │ VALIDATED  │  2   │ New status: pre-calculation validation passed.  │
    │ CALCULATING│  2   │ Legacy in-flight status (same rank as VALIDATED)│
    │ PARTIAL    │  3   │ Calculation complete; some employees failed.    │
    │ CALCULATED │  4   │ Calculation complete; all employees succeeded.  │
    │ APPROVED   │  5   │ Authorised approver signed off.                 │
    │ LOCKED     │  6   │ Finalized; no further changes allowed.          │
    │ PAID       │  7   │ Terminal state; disbursement confirmed.         │
    └────────────┴──────┴─────────────────────────────────────────────────┘

Enforcement rules
-----------------
1. Status cannot move backwards (new_rank < old_rank is rejected).
2. PAID is terminal — any update FROM PAID is rejected (also enforced by the
   separate trg_prevent_paid_run_update trigger from migration d9828ee962a2).
3. INSERT may set status to DRAFT only.
4. Unknown status values are rejected with a clear error.

Triggers created
----------------
  trg_validate_payroll_status_transition
      BEFORE UPDATE OF status ON payroll_run — enforces rules 1, 2, 4.

  trg_enforce_payroll_run_initial_status
      BEFORE INSERT ON payroll_run — enforces rule 3.

Triggers dropped
----------------
  trg_payroll_run_state_machine          (migration 9901bc4ed0c5, obsolete)
  Function enforce_payroll_run_state_machine() (same migration, dropped)
"""

from typing import Sequence, Union

from alembic import op


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "e2f3a4b5c6d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Drop the legacy trigger/function from migration 9901bc4ed0c5.
    # That function used obsolete status values (PROCESSING, COMPLETED,
    # FAILED, CANCELLED) that no longer exist in the codebase.  Its IF
    # conditions never matched current statuses, making it a silent no-op.
    # ------------------------------------------------------------------
    op.execute(
        "DROP TRIGGER IF EXISTS trg_payroll_run_state_machine ON payroll_run;"
    )
    op.execute(
        "DROP FUNCTION IF EXISTS enforce_payroll_run_state_machine();"
    )

    # ------------------------------------------------------------------
    # 1. Trigger function — UPDATE guard
    #
    # Assigns each known status a rank and rejects any transition where
    # the new rank is strictly less than the old rank (backward movement).
    # Transitions at the same rank level (e.g. PARTIAL → CALCULATED via
    # retry, which moves from rank 3 to rank 4) are forward-only.
    # Note: PARTIAL(3) → CALCULATED(4) is forward; CALCULATED(4) →
    # PARTIAL(3) is backward and is correctly blocked.
    # ------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION validate_payroll_status_transition()
        RETURNS trigger AS $$
        DECLARE
            v_old_rank INT;
            v_new_rank INT;
        BEGIN
            -- Resolve lifecycle rank for the current status.
            SELECT position INTO v_old_rank
            FROM (VALUES
                ('DRAFT',       1),
                ('VALIDATED',   2),
                ('CALCULATING', 2),
                ('PARTIAL',     3),
                ('CALCULATED',  4),
                ('APPROVED',    5),
                ('LOCKED',      6),
                ('PAID',        7)
            ) AS lifecycle(status, position)
            WHERE status = OLD.status;

            -- Resolve lifecycle rank for the target status.
            SELECT position INTO v_new_rank
            FROM (VALUES
                ('DRAFT',       1),
                ('VALIDATED',   2),
                ('CALCULATING', 2),
                ('PARTIAL',     3),
                ('CALCULATED',  4),
                ('APPROVED',    5),
                ('LOCKED',      6),
                ('PAID',        7)
            ) AS lifecycle(status, position)
            WHERE status = NEW.status;

            -- Reject unknown status values immediately.
            IF v_old_rank IS NULL THEN
                RAISE EXCEPTION
                    'Unknown payroll run status: %. '
                    'Valid statuses: DRAFT, VALIDATED, CALCULATING, PARTIAL, '
                    'CALCULATED, APPROVED, LOCKED, PAID.',
                    OLD.status;
            END IF;

            IF v_new_rank IS NULL THEN
                RAISE EXCEPTION
                    'Unknown payroll run status: %. '
                    'Valid statuses: DRAFT, VALIDATED, CALCULATING, PARTIAL, '
                    'CALCULATED, APPROVED, LOCKED, PAID.',
                    NEW.status;
            END IF;

            -- Enforce forward-only progression.
            -- PAID (rank 7) is terminal: nothing has a higher rank,
            -- so any transition FROM PAID fails here.
            IF v_new_rank < v_old_rank THEN
                RAISE EXCEPTION
                    'Invalid payroll run status transition: % → %. '
                    'Status cannot move backwards. '
                    'Allowed forward transitions: '
                    'DRAFT → VALIDATED → CALCULATED → APPROVED → PAID.',
                    OLD.status, NEW.status;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # ------------------------------------------------------------------
    # 2. Attach BEFORE UPDATE trigger
    #
    # Fires only when the status column is actually changing, avoiding
    # unnecessary overhead on unrelated column updates.
    # ------------------------------------------------------------------
    op.execute(
        "DROP TRIGGER IF EXISTS trg_validate_payroll_status_transition "
        "ON payroll_run;"
    )
    op.execute("""
        CREATE TRIGGER trg_validate_payroll_status_transition
        BEFORE UPDATE OF status ON payroll_run
        FOR EACH ROW
        WHEN (OLD.status IS DISTINCT FROM NEW.status)
        EXECUTE FUNCTION validate_payroll_status_transition();
    """)

    # ------------------------------------------------------------------
    # 3. Trigger function — INSERT guard
    #
    # Ensures every new payroll_run is created in the initial DRAFT state.
    # The application then advances the run through the lifecycle via
    # explicit UPDATE calls, each of which passes through the UPDATE
    # trigger above.
    # ------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION enforce_payroll_run_initial_status()
        RETURNS trigger AS $$
        BEGIN
            IF NEW.status <> 'DRAFT' THEN
                RAISE EXCEPTION
                    'New payroll runs must be created with status DRAFT. Got: %.',
                    NEW.status;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # ------------------------------------------------------------------
    # 4. Attach BEFORE INSERT trigger
    # ------------------------------------------------------------------
    op.execute(
        "DROP TRIGGER IF EXISTS trg_enforce_payroll_run_initial_status "
        "ON payroll_run;"
    )
    op.execute("""
        CREATE TRIGGER trg_enforce_payroll_run_initial_status
        BEFORE INSERT ON payroll_run
        FOR EACH ROW
        EXECUTE FUNCTION enforce_payroll_run_initial_status();
    """)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_enforce_payroll_run_initial_status "
        "ON payroll_run;"
    )
    op.execute("DROP FUNCTION IF EXISTS enforce_payroll_run_initial_status();")

    op.execute(
        "DROP TRIGGER IF EXISTS trg_validate_payroll_status_transition "
        "ON payroll_run;"
    )
    op.execute("DROP FUNCTION IF EXISTS validate_payroll_status_transition();")

    # Restore the legacy trigger so downgrade is reversible.
    op.execute("""
        CREATE OR REPLACE FUNCTION enforce_payroll_run_state_machine()
        RETURNS trigger AS $$
        BEGIN
            IF OLD.status = 'PAID' THEN
                RAISE EXCEPTION 'Cannot modify a PAID payroll run';
            END IF;
            IF OLD.status = 'DRAFT' AND NEW.status NOT IN ('PROCESSING', 'CANCELLED') THEN
                RAISE EXCEPTION 'Invalid status transition from DRAFT to %', NEW.status;
            END IF;
            IF OLD.status = 'PROCESSING' AND NEW.status NOT IN ('COMPLETED', 'FAILED') THEN
                RAISE EXCEPTION 'Invalid status transition from PROCESSING to %', NEW.status;
            END IF;
            IF OLD.status = 'COMPLETED' AND NEW.status <> 'PAID' THEN
                RAISE EXCEPTION 'Invalid status transition from COMPLETED to %', NEW.status;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trg_payroll_run_state_machine
        BEFORE UPDATE OF status ON payroll_run
        FOR EACH ROW
        WHEN (OLD.status IS DISTINCT FROM NEW.status)
        EXECUTE FUNCTION enforce_payroll_run_state_machine();
    """)
