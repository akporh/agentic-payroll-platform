"""
Payroll Run Repository.
"""

from decimal import Decimal

from psycopg2.extras import Json
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from backend.infra.db.session import SessionLocal


def save_payroll_run(
    payroll_run_id: str,
    workspace_id: str,
    status: str,
    rules_context_snapshot: dict,
    idempotency_key: str | None = None,
    period_start: str | None = None,
    period_end: str | None = None,
    total_gross_pay: Decimal = Decimal("0"),
    total_tax: Decimal = Decimal("0"),
    total_net_pay: Decimal = Decimal("0"),
    retry_strategy: str = "PER_EMPLOYEE",
):
    """Insert a new payroll_run row and advance it to the target status.

    Args:
        payroll_run_id: Primary key for the run.
        workspace_id: Owning workspace.
        status: Target lifecycle status (e.g. "CALCULATED" or "PARTIAL").
            The row is always inserted with status='DRAFT' to satisfy
            trg_enforce_payroll_run_initial_status, then immediately
            updated to this value via a separate UPDATE that passes through
            trg_validate_payroll_status_transition.
        rules_context_snapshot: Snapshot of rules used for the run.
        idempotency_key: Optional caller-supplied key.  When provided, the
            partial unique index ux_payroll_run_idempotency prevents a second
            INSERT with the same (workspace_id, idempotency_key) pair.
        period_start: Optional ISO-format start date of the pay period.
        period_end: Optional ISO-format end date of the pay period.
        total_gross_pay: Sum of all gross salary components across all employees.
        total_tax: Total PAYE tax deducted across all employees.
        total_net_pay: Total net pay across all employees (gross minus tax).

    Raises:
        ValueError: If a duplicate idempotency key or duplicate pay period is
            detected (wraps the underlying IntegrityError so callers can
            surface a clean 409 response without catching DB-level exceptions).
    """
    db = SessionLocal()

    try:
        # INSERT with DRAFT status — required by trg_enforce_payroll_run_initial_status.
        # All financial columns are included here so the row is complete from
        # the first write; only the status column changes in the UPDATE below.
        db.execute(
            text("""
            INSERT INTO payroll_run (
                payroll_run_id,
                workspace_id,
                status,
                rules_context_snapshot,
                idempotency_key,
                period_start,
                period_end,
                total_gross_pay,
                total_deduction,
                total_tax,
                total_net_pay,
                retry_strategy
            )
            VALUES (
                :payroll_run_id,
                :workspace_id,
                'DRAFT',
                :rules_context_snapshot,
                :idempotency_key,
                :period_start,
                :period_end,
                :total_gross_pay,
                :total_deduction,
                :total_tax,
                :total_net_pay,
                :retry_strategy
            )
            """),
            {
                "payroll_run_id": payroll_run_id,
                "workspace_id": workspace_id,
                "rules_context_snapshot": Json(rules_context_snapshot),
                "idempotency_key": idempotency_key,
                "period_start": period_start,
                "period_end": period_end,
                "total_gross_pay": total_gross_pay,
                "total_deduction": total_tax,
                "total_tax": total_tax,
                "total_net_pay": total_net_pay,
                "retry_strategy": retry_strategy,
            },
        )

        # Advance from DRAFT to the computed final status via an UPDATE that
        # passes through trg_validate_payroll_status_transition.  The trigger
        # allows any forward movement (DRAFT rank 1 → CALCULATED rank 4, or
        # DRAFT rank 1 → PARTIAL rank 3), so this single UPDATE is sufficient.
        if status != "DRAFT":
            db.execute(
                text(
                    "UPDATE payroll_run SET status = :status "
                    "WHERE payroll_run_id = :rid"
                ),
                {"status": status, "rid": payroll_run_id},
            )

        db.commit()

    except IntegrityError as exc:
        db.rollback()
        raise ValueError(
            f"Duplicate payroll run detected (idempotency_key or period conflict): {exc.orig}"
        ) from exc

    finally:
        db.close()
