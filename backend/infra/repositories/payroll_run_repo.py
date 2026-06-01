"""
Payroll Run Repository.
"""

import json
from decimal import Decimal

from psycopg2.extras import Json
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from backend.infra.db.session import SessionLocal


def _decimal_safe_dumps(obj: object) -> str:
    """JSON serializer that converts Decimal to float (not str) for JSONB compatibility."""
    class _Enc(json.JSONEncoder):
        def default(self, o: object) -> object:
            if isinstance(o, Decimal):
                return float(o)
            return super().default(o)
    return json.dumps(obj, cls=_Enc)


def _Json(obj: object) -> Json:
    return Json(obj, dumps=_decimal_safe_dumps)


def create_draft_payroll_run(
    payroll_run_id: str,
    workspace_id: str,
    rules_context_snapshot: dict,
    idempotency_key: str | None = None,
    period_start: str | None = None,
    period_end: str | None = None,
    retry_strategy: str = "PER_EMPLOYEE",
    rule_set_id: str | None = None,
    statutory_effective_date: str | None = None,
    run_type: str = "REGULAR",
    public_holidays_snapshot: list | None = None,
) -> None:
    """INSERT a DRAFT payroll_run row before execution begins.

    rules_context_snapshot is written here (not in finalise_payroll_run) because
    the DB trigger trg_run_snapshot_immutable fires on any UPDATE to that column
    after initial INSERT — so it must be written once, in the INSERT.

    Raises:
        ValueError: On duplicate idempotency_key or period conflict.
    """
    db = SessionLocal()
    try:
        db.execute(
            text("""
                INSERT INTO payroll_run (
                    payroll_run_id, workspace_id, status,
                    rules_context_snapshot,
                    idempotency_key, period_start, period_end,
                    retry_strategy, rule_set_id, statutory_effective_date,
                    run_type, public_holidays_snapshot
                )
                VALUES (
                    :run_id, :wid, 'DRAFT',
                    :snapshot,
                    :ikey, :ps, :pe,
                    :strategy, :rset, :sed,
                    :rtype, :ph_snap
                )
            """),
            {
                "run_id":    payroll_run_id,
                "wid":       workspace_id,
                "snapshot":  _Json(rules_context_snapshot),
                "ikey":      idempotency_key,
                "ps":        period_start,
                "pe":        period_end,
                "strategy":  retry_strategy,
                "rset":      rule_set_id,
                "sed":       statutory_effective_date,
                "rtype":     run_type,
                "ph_snap":   _Json(public_holidays_snapshot) if public_holidays_snapshot is not None else None,
            },
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError(
            f"Duplicate payroll run detected (idempotency_key or period conflict): {exc.orig}"
        ) from exc
    finally:
        db.close()


def finalise_payroll_run(
    payroll_run_id: str,
    status: str,
    total_gross_pay: Decimal = Decimal("0"),
    total_deduction: Decimal = Decimal("0"),
    total_tax: Decimal = Decimal("0"),
    total_net_pay: Decimal = Decimal("0"),
) -> None:
    """UPDATE a DRAFT payroll_run row with totals + final status after execution.

    rules_context_snapshot is NOT updated here — it was written in the DRAFT INSERT
    by create_draft_payroll_run() and is immutable (trg_run_snapshot_immutable).
    """
    db = SessionLocal()
    try:
        db.execute(
            text("""
                UPDATE payroll_run
                SET
                    status          = :status,
                    total_gross_pay = :gross,
                    total_deduction = :deduction,
                    total_tax       = :tax,
                    total_net_pay   = :net
                WHERE payroll_run_id = :run_id
            """),
            {
                "status":    status,
                "gross":     total_gross_pay,
                "deduction": total_deduction,
                "tax":       total_tax,
                "net":       total_net_pay,
                "run_id":    payroll_run_id,
            },
        )
        db.commit()
    finally:
        db.close()
