"""Add FAILED payroll_run status + error_message column (05-001 remediation)

Revision ID: b8c9d0e1f2a3
Revises: ef2a3b4c5d6e
Create Date: 2026-07-12

Audit remediation for Stage 05 finding 05-001: snapshot creation
(component_metadata_snapshot / client_component_metadata_snapshot /
employee_contract_snapshot) previously ran in a background task with its
exception silently logged and swallowed, after which calculation proceeded
anyway. A run whose snapshot failed to persist would still calculate and
complete normally, only surfacing the problem later — and only as a
retry-time hard-fail with no visible cause — the first time an operator
tried to retry a FAILED employee on it.

This migration adds a new, terminal `FAILED` status (reached only from
DRAFT — snapshot creation runs before the DRAFT -> CALCULATING transition,
so a run whose snapshot failed never reaches CALCULATING) and a nullable
`error_message` column so the failure reason is queryable via the existing
GET /payroll/runs/{run_id} route, not just server logs.

`FAILED` is a new status value, not an overload of an existing one, per
CLAUDE.md's "New status/enum values are introduced, never overloaded with
new meaning" rule. It is given the same lifecycle rank as DRAFT (1) in
validate_payroll_status_transition(), since it is reachable only from DRAFT
and rank must not decrease on any transition.
"""

from typing import Sequence, Union

from alembic import op


revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, Sequence[str], None] = "ef2a3b4c5d6e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. error_message column — guarded per CLAUDE.md ADD COLUMN convention.
    # ------------------------------------------------------------------
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE payroll_run ADD COLUMN error_message TEXT;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)

    # ------------------------------------------------------------------
    # 2. Add FAILED (rank 1, tied with DRAFT) to the transition-validation
    #    function. CREATE OR REPLACE is idempotent/safe to re-run.
    # ------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION validate_payroll_status_transition()
        RETURNS trigger AS $$
        DECLARE
            v_old_rank INT;
            v_new_rank INT;
        BEGIN
            SELECT position INTO v_old_rank
            FROM (VALUES
                ('DRAFT',       1),
                ('FAILED',      1),
                ('VALIDATED',   2),
                ('CALCULATING', 2),
                ('PARTIAL',     3),
                ('CALCULATED',  4),
                ('APPROVED',    5),
                ('LOCKED',      6),
                ('PAID',        7)
            ) AS lifecycle(status, position)
            WHERE status = OLD.status;

            SELECT position INTO v_new_rank
            FROM (VALUES
                ('DRAFT',       1),
                ('FAILED',      1),
                ('VALIDATED',   2),
                ('CALCULATING', 2),
                ('PARTIAL',     3),
                ('CALCULATED',  4),
                ('APPROVED',    5),
                ('LOCKED',      6),
                ('PAID',        7)
            ) AS lifecycle(status, position)
            WHERE status = NEW.status;

            IF v_old_rank IS NULL THEN
                RAISE EXCEPTION
                    'Unknown payroll run status: %. '
                    'Valid statuses: DRAFT, FAILED, VALIDATED, CALCULATING, PARTIAL, '
                    'CALCULATED, APPROVED, LOCKED, PAID.',
                    OLD.status;
            END IF;

            IF v_new_rank IS NULL THEN
                RAISE EXCEPTION
                    'Unknown payroll run status: %. '
                    'Valid statuses: DRAFT, FAILED, VALIDATED, CALCULATING, PARTIAL, '
                    'CALCULATED, APPROVED, LOCKED, PAID.',
                    NEW.status;
            END IF;

            IF v_new_rank < v_old_rank THEN
                RAISE EXCEPTION
                    'Invalid payroll run status transition: % → %. '
                    'Status cannot move backwards. '
                    'Allowed forward transitions: '
                    'DRAFT → VALIDATED → CALCULATED → APPROVED → PAID '
                    '(or DRAFT → FAILED if a calculation precondition fails).',
                    OLD.status, NEW.status;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    # Restore the pre-05-001 transition function (no FAILED rank).
    op.execute("""
        CREATE OR REPLACE FUNCTION validate_payroll_status_transition()
        RETURNS trigger AS $$
        DECLARE
            v_old_rank INT;
            v_new_rank INT;
        BEGIN
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

    op.execute("""
        DO $$ BEGIN
            ALTER TABLE payroll_run DROP COLUMN error_message;
        EXCEPTION WHEN undefined_column THEN NULL;
        END $$;
    """)
