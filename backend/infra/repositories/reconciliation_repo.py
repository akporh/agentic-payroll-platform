"""
Reconciliation Repository.

Raw-SQL persistence layer for payroll_reconciliation rows.
"""

from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from backend.infra.db.session import SessionLocal


def insert_reconciliation(
    *,
    payroll_run_id: str,
    expected_total: Decimal,
    actual_total: Decimal | None,
    status: str,
) -> dict:
    """Insert a new payroll_reconciliation row.

    Sets reconciled_at to now() for MATCHED/MISMATCH; leaves it NULL for PENDING.

    Returns the created row as a dict.

    Raises:
        ValueError: If a reconciliation record already exists for this run.
    """
    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                INSERT INTO payroll_reconciliation (
                    payroll_run_id,
                    expected_total,
                    actual_total,
                    status,
                    reconciled_at
                )
                VALUES (
                    :payroll_run_id,
                    :expected_total,
                    :actual_total,
                    :status,
                    CASE WHEN :status <> 'PENDING' THEN now() ELSE NULL END
                )
                RETURNING id, payroll_run_id, expected_total, actual_total,
                          status, reconciled_at, created_at
            """),
            {
                "payroll_run_id": payroll_run_id,
                "expected_total": expected_total,
                "actual_total":   actual_total,
                "status":         status,
            },
        ).fetchone()

        db.commit()

        return {
            "id":              str(row[0]),
            "payroll_run_id":  str(row[1]),
            "expected_total":  row[2],
            "actual_total":    row[3],
            "status":          row[4],
            "reconciled_at":   row[5].isoformat() if row[5] else None,
            "created_at":      row[6].isoformat() if row[6] else None,
        }

    except IntegrityError as exc:
        db.rollback()
        raise ValueError(
            f"A reconciliation record already exists for run {payroll_run_id}."
        ) from exc

    finally:
        db.close()


def get_reconciliation(payroll_run_id: str) -> dict | None:
    """Fetch the reconciliation record for a run, or None if not found."""
    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                SELECT id, payroll_run_id, expected_total, actual_total,
                       status, reconciled_at, created_at
                FROM   payroll_reconciliation
                WHERE  payroll_run_id = :rid
            """),
            {"rid": payroll_run_id},
        ).fetchone()

        if row is None:
            return None

        return {
            "id":              str(row[0]),
            "payroll_run_id":  str(row[1]),
            "expected_total":  row[2],
            "actual_total":    row[3],
            "status":          row[4],
            "reconciled_at":   row[5].isoformat() if row[5] else None,
            "created_at":      row[6].isoformat() if row[6] else None,
        }

    finally:
        db.close()
