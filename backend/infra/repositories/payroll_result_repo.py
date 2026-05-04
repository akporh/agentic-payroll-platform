"""
Payroll Result Repository.

Responsible for persisting payroll_result records.
Handles JSON sanitization at infrastructure boundary.
"""

from sqlalchemy import text
from psycopg2.extras import Json
from backend.infra.db.session import SessionLocal
import json


def _sanitize_json(payload: dict | None) -> dict:
    """
    Convert Decimal, UUID, etc. into JSON-safe values.

    Decimal is serialised as a JSON *number* (via float) so that JSONB
    columns remain queryable with val::text::numeric casts.  All other
    non-serialisable types fall back to str().
    """
    if payload is None:
        return {}

    from decimal import Decimal as _Decimal

    def _default(obj):
        if isinstance(obj, _Decimal):
            return float(obj)
        return str(obj)

    return json.loads(json.dumps(payload, default=_default))


def get_employee_context_from_result(db, payroll_run_id: str, employee_id: str) -> dict:
    """Read per_employee_context_json from an existing payroll_result row.

    Used by retry paths (D4/D5) to recover frozen employee eligibility flags
    (e.g. is_union_member) before the result row is deleted and re-inserted.
    Returns {} for rows that predate the migration or have NULL context.
    """
    row = db.execute(
        text("""
            SELECT per_employee_context_json
            FROM payroll_result
            WHERE payroll_run_id = :run_id
              AND employee_id    = :eid
        """),
        {"run_id": payroll_run_id, "eid": employee_id},
    ).fetchone()
    if row is None:
        return {}
    return row[0] or {}


def save_payroll_result(
    payroll_run_id: str,
    employee_id: str,
    status: str,
    payroll_output: dict | None,
    error_message: str | None,
    component_trace: list | None = None,
    employee_context: dict | None = None,
):
    """
    Persist a single payroll result.
    """

    db = SessionLocal()

    if status == "SUCCESS" and payroll_output is not None:
        payroll_result = payroll_output["payroll_result"]

        gross_components = _sanitize_json(
            payroll_result["gross_components_jsonb"]
        )

        deductions = _sanitize_json(
            payroll_result["deductions_jsonb"]
        )

        snapshot = _sanitize_json(
            payroll_result["calculations_snapshot_json"]
        )

        net_pay = payroll_result["net_pay"]

        # Prefer trace from payroll_result; caller-supplied trace is a fallback
        component_trace = (
            payroll_result.get("component_trace_jsonb") or component_trace
        )

    else:
        gross_components = {}
        deductions = {}
        snapshot = {}
        net_pay = 0

    trace_value = _sanitize_json(component_trace) if component_trace else None

    db.execute(
        text("""
        INSERT INTO payroll_result (
            payroll_result_id,
            payroll_run_id,
            employee_id,
            gross_components_jsonb,
            deductions_jsonb,
            net_pay,
            calculations_snapshot_json,
            component_trace_jsonb,
            status,
            error_message,
            per_employee_context_json
        )
        VALUES (
            gen_random_uuid(),
            :payroll_run_id,
            :employee_id,
            :gross_components,
            :deductions,
            :net_pay,
            :snapshot,
            :trace,
            :status,
            :error_message,
            :per_employee_context_json
        )
        """),
        {
            "payroll_run_id": payroll_run_id,
            "employee_id": employee_id,
            "gross_components": Json(gross_components),
            "deductions": Json(deductions),
            "net_pay": net_pay,
            "snapshot": Json(snapshot),
            "trace": Json(trace_value) if trace_value is not None else None,
            "status": status,
            "error_message": error_message,
            "per_employee_context_json": (
                Json(_sanitize_json(employee_context)) if employee_context else None
            ),
        }
    )

    db.commit()
    db.close()