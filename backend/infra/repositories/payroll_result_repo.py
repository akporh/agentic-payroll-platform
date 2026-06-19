"""
Payroll Result Repository.

Responsible for persisting payroll_result records.
Handles JSON sanitization at infrastructure boundary.
"""

import uuid

from sqlalchemy import text
from psycopg2.extras import Json, execute_values
from backend.infra.db.session import SessionLocal, engine
from backend.infra.json_utils import sanitize_jsonb as _sanitize_json


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


def save_payroll_results_bulk(
    payroll_run_id: str,
    results: list[dict],
    salary_inputs_by_employee: dict | None = None,
) -> None:
    """Persist all payroll results for a run in a single connection and transaction.

    Replaces 175 individual save_payroll_result calls (175 connections, 175
    commits) with one psycopg2 execute_values call — one connection, one
    multi-row INSERT, one commit.
    """
    if not results:
        return

    rows = []
    for r in results:
        status = r["status"]
        output = r.get("output")
        employee_context = r.get("employee_context")

        if status == "SUCCESS" and output is not None:
            pr = output["payroll_result"]
            gross_components = _sanitize_json(pr["gross_components_jsonb"])
            deductions = _sanitize_json(pr["deductions_jsonb"])
            snapshot = _sanitize_json(pr["calculations_snapshot_json"])
            net_pay = pr["net_pay"]
            component_trace = pr.get("component_trace_jsonb")
        else:
            gross_components = {}
            deductions = {}
            snapshot = {}
            net_pay = 0
            component_trace = None

        trace_value = _sanitize_json(component_trace) if component_trace else None
        sal_snap = (salary_inputs_by_employee or {}).get(r["employee_id"], {})

        rows.append((
            str(uuid.uuid4()),
            payroll_run_id,
            r["employee_id"],
            Json(gross_components),
            Json(deductions),
            net_pay,
            Json(snapshot),
            Json(trace_value) if trace_value is not None else None,
            status,
            r.get("error"),
            Json(_sanitize_json(employee_context)) if employee_context else None,
            Json(sal_snap),
        ))

    raw_conn = engine.raw_connection()
    try:
        cursor = raw_conn.cursor()
        execute_values(
            cursor,
            """
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
                per_employee_context_json,
                salary_inputs_snapshot
            ) VALUES %s
            """,
            rows,
        )
        raw_conn.commit()
    finally:
        cursor.close()
        raw_conn.close()


def save_payroll_result(
    payroll_run_id: str,
    employee_id: str,
    status: str,
    payroll_output: dict | None,
    error_message: str | None,
    component_trace: list | None = None,
    employee_context: dict | None = None,
    salary_inputs_snapshot: dict | None = None,
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
            per_employee_context_json,
            salary_inputs_snapshot
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
            :per_employee_context_json,
            :salary_inputs_snapshot
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
            "salary_inputs_snapshot": Json(salary_inputs_snapshot or {}),
        }
    )

    db.commit()
    db.close()