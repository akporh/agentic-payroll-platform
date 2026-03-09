"""Prevent payroll_result mutation after calculation

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-03-06

Once a payroll run reaches CALCULATED (or any subsequent status), the
financial results stored in payroll_result must be immutable.  This
migration adds a trigger function and attaches BEFORE UPDATE / BEFORE
DELETE triggers to payroll_result.

Relationship to existing triggers
----------------------------------
A prior migration (3da637afb11b) added trg_prevent_paid_result_update /
trg_prevent_paid_result_delete, which only block mutations when the parent
run is PAID.  The new trigger function introduced here is stricter: it
blocks mutations from CALCULATED onward (CALCULATED → APPROVED → LOCKED
→ PAID), enforcing immutability as soon as the engine has finished its
calculation — not just at the terminal PAID state.

Statuses that block mutation
-----------------------------
  CALCULATED  — engine finished; results are under review
  APPROVED    — authorised approver signed off
  LOCKED      — finalized; no further changes allowed
  PAID        — terminal state (also covered by existing trigger)

Statuses that permit mutation
------------------------------
  DRAFT       — run is being prepared (no results yet)
  CALCULATING — engine is actively running
  PARTIAL     — some employees failed; retry will UPDATE failed results

Note on payroll_line_item
--------------------------
The payroll_line_item table does not exist in this schema.  All line-level
data is stored as JSONB inside payroll_result.gross_components_jsonb and
payroll_result.deductions_jsonb.  No trigger is attached to a non-existent
table.
"""

from typing import Sequence, Union

from alembic import op


revision: str = "e2f3a4b5c6d7"
down_revision: Union[str, Sequence[str], None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Trigger function
    # ------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_payroll_result_mutation()
        RETURNS trigger AS $$
        DECLARE
            v_run_id UUID;
            v_status TEXT;
        BEGIN
            -- Works for both UPDATE (NEW is available) and DELETE (NEW is NULL)
            v_run_id := COALESCE(NEW.payroll_run_id, OLD.payroll_run_id);

            SELECT status INTO v_status
            FROM   payroll_run
            WHERE  payroll_run_id = v_run_id;

            IF v_status IN ('CALCULATED', 'APPROVED', 'LOCKED', 'PAID') THEN
                RAISE EXCEPTION
                    'Payroll results are immutable after calculation. '
                    'Run % has status %.',
                    v_run_id,
                    v_status;
            END IF;

            -- Allow the operation
            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
    """)

    # ------------------------------------------------------------------
    # 2. Attach BEFORE UPDATE trigger to payroll_result
    # ------------------------------------------------------------------
    op.execute("""
        CREATE TRIGGER trg_prevent_calculated_result_update
        BEFORE UPDATE ON payroll_result
        FOR EACH ROW
        EXECUTE FUNCTION prevent_payroll_result_mutation();
    """)

    # ------------------------------------------------------------------
    # 3. Attach BEFORE DELETE trigger to payroll_result
    # ------------------------------------------------------------------
    op.execute("""
        CREATE TRIGGER trg_prevent_calculated_result_delete
        BEFORE DELETE ON payroll_result
        FOR EACH ROW
        EXECUTE FUNCTION prevent_payroll_result_mutation();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_calculated_result_delete ON payroll_result;")
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_calculated_result_update ON payroll_result;")
    op.execute("DROP FUNCTION IF EXISTS prevent_payroll_result_mutation();")
