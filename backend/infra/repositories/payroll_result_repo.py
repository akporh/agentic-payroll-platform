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
    """
    if payload is None:
        return {}

    return json.loads(json.dumps(payload, default=str))


def save_payroll_result(
    payroll_run_id: str,
    employee_id: str,
    status: str,
    payroll_output: dict | None,
    error_message: str | None,
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

    else:
        gross_components = {}
        deductions = {}
        snapshot = {}
        net_pay = 0

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
            status,
            error_message
        )
        VALUES (
            gen_random_uuid(),
            :payroll_run_id,
            :employee_id,
            :gross_components,
            :deductions,
            :net_pay,
            :snapshot,
            :status,
            :error_message
        )
        """),
        {
            "payroll_run_id": payroll_run_id,
            "employee_id": employee_id,
            "gross_components": Json(gross_components),
            "deductions": Json(deductions),
            "net_pay": net_pay,
            "snapshot": Json(snapshot),
            "status": status,
            "error_message": error_message,
        }
    )

    db.commit()
    db.close()