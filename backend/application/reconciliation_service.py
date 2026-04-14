"""
Reconciliation Service.

Phase 1 manual reconciliation: compares the payroll engine's expected total
(payroll_run.total_net_pay) against an externally supplied actual_total and
records the outcome as MATCHED or MISMATCH.
"""

from decimal import Decimal

from sqlalchemy import text

from backend.infra.db.session import SessionLocal
from backend.infra.repositories.reconciliation_repo import (
    insert_reconciliation,
    get_reconciliation,
    update_reconciliation,
)


def reconcile_payroll_run(payroll_run_id: str, actual_total: Decimal) -> dict:
    """Compare the engine total against the externally paid amount and persist
    the result.

    Steps
    -----
    1. Load expected_total from payroll_run.total_net_pay.
    2. Compare expected_total vs actual_total.
    3. Insert a payroll_reconciliation row with status MATCHED or MISMATCH.
    4. Return the created record.

    Args:
        payroll_run_id: UUID of the payroll run to reconcile.
        actual_total:   Amount confirmed as paid externally (e.g. bank transfer
                        total or manual confirmation).

    Returns:
        dict with keys: id, payroll_run_id, expected_total, actual_total,
                        status, reconciled_at, created_at.

    Raises:
        ValueError: Run not found, or reconciliation already exists for this run.
    """
    actual_total = Decimal(str(actual_total))

    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                SELECT total_net_pay, status
                FROM   payroll_run
                WHERE  payroll_run_id = :rid
            """),
            {"rid": payroll_run_id},
        ).fetchone()
    finally:
        db.close()

    if row is None:
        raise ValueError(f"Payroll run {payroll_run_id} not found.")

    if row[1] != "LOCKED":
        raise ValueError(
            f"Reconciliation requires a LOCKED run. Current status: {row[1]}."
        )

    expected_total = Decimal(str(row[0]))
    status = "MATCHED" if actual_total == expected_total else "MISMATCH"

    return insert_reconciliation(
        payroll_run_id=payroll_run_id,
        expected_total=expected_total,
        actual_total=actual_total,
        status=status,
    )


def get_reconciliation_status(payroll_run_id: str) -> dict | None:
    """Return the current reconciliation record for a run, or None."""
    return get_reconciliation(payroll_run_id)


def resolve_reconciliation(payroll_run_id: str, notes: str, resolved_by: str) -> dict:
    """Mark a MISMATCH reconciliation as resolved by the operator.

    Args:
        payroll_run_id: UUID of the payroll run.
        notes:          Explanation of why the discrepancy is considered resolved.
        resolved_by:    Identifier of the operator performing the resolution.

    Returns:
        Updated reconciliation record dict.

    Raises:
        ValueError: If no MISMATCH record exists for this run.
    """
    return update_reconciliation(
        payroll_run_id=payroll_run_id,
        notes=notes,
        resolved_by=resolved_by,
    )
