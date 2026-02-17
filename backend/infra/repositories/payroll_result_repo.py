from psycopg2.extras import Json
from sqlalchemy import text
from backend.infra.db.session import SessionLocal


def save_payroll_result(payroll_run_id: str, employee_id: str, result: dict):
    db = SessionLocal()

    db.execute(
        text("""
        INSERT INTO payroll_result (
            payroll_result_id,
            payroll_run_id,
            employee_id,
            gross_components_jsonb,
            deductions_jsonb,
            net_pay,
            calculations_snapshot_json
        )
        VALUES (
            gen_random_uuid(),
            :payroll_run_id,
            :employee_id,
            :gross_components,
            :deductions,
            :net_pay,
            :snapshot
        )
        """),
        {
            "payroll_run_id": payroll_run_id,
            "employee_id": employee_id,
            "gross_components": Json(result["gross_components_jsonb"]),
	    "deductions": Json(result["deductions_jsonb"]),
            "net_pay": result["net_pay"],
            "snapshot": Json(result["calculations_snapshot_json"]),
        }
    )

    db.commit()
    db.close()

