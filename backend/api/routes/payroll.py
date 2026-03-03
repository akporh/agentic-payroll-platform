"""
Payroll API Routes.

Exposes endpoints for triggering payroll runs.
"""

import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from backend.infra.db.session import SessionLocal
from backend.application.payroll_run_service import execute_and_persist

router = APIRouter()


@router.post("/payroll/run")
def run_payroll(payload: dict):
    """
    Trigger a payroll run for a workspace.
    """

    workspace_id = payload.get("workspace_id")

    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id required")

    db = SessionLocal()

    # --- Verify workspace exists ---
    workspace = db.execute(
        text("SELECT workspace_id FROM workspace WHERE workspace_id = :wid"),
        {"wid": workspace_id}
    ).fetchone()

    if not workspace:
        db.close()
        raise HTTPException(status_code=404, detail="Workspace not found")

    # --- Load Employees ---
    employee_rows = db.execute(text("""
        SELECT e.employee_id, sd.components_jsonb
        FROM employee e
        JOIN employee_contract ec
          ON e.employee_id = ec.employee_id
        JOIN salary_definition sd
          ON ec.salary_definition_id = sd.salary_definition_id
        WHERE e.workspace_id = :workspace_id
          AND e.status = 'ACTIVE'
          AND (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
    """), {"workspace_id": workspace_id}).fetchall()

    employees = []
    for row in employee_rows:
        employees.append({
            "employee_id": str(row[0]),
            "components": [
                {"code": k, "amount": v["amount"]}
                for k, v in row[1].items()
            ],
        })

    if not employees:
        db.close()
        raise HTTPException(status_code=400, detail="No active employees found")
    
    print("Employees being processed:", len(employees))
    for e in employees:
        print(e["employee_id"])


    # --- Load Tax Bands ---
    tax_rows = db.execute(text("""
        SELECT lower_limit, upper_limit, rate
        FROM tax_band
        ORDER BY lower_limit
    """)).fetchall()

    tax_bands = [
        {"lower_limit": r[0], "upper_limit": r[1], "rate": r[2]}
        for r in tax_rows
    ]

    # --- Load Latest Statutory Rule ---
    stat_row = db.execute(text("""
        SELECT statutory_rule_id, version
        FROM statutory_rule
        ORDER BY version DESC
        LIMIT 1
    """)).fetchone()

    if not stat_row:
        db.close()
        raise HTTPException(status_code=400, detail="No statutory rule found")

    statutory_rule_id = str(stat_row[0])
    statutory_version = stat_row[1]

    # --- Load Active Payroll Rules ---
    rule_rows = db.execute(text("""
        SELECT rule_id
        FROM payroll_rule
        WHERE is_active = TRUE
    """)).fetchall()

    payroll_rule_ids = [str(r[0]) for r in rule_rows]

    db.close()

    payroll_run_id = str(uuid.uuid4())

    result = execute_and_persist(
        payroll_run_id=payroll_run_id,
        workspace_id=workspace_id,
        employees=employees,
        tax_bands=tax_bands,
        statutory_rule_id=statutory_rule_id,
        statutory_version=statutory_version,
        payroll_rule_ids=payroll_rule_ids,
        performed_by="admin@internal",
        execution_mode="isolated",
    )

    return {
        "status": "success",
        "payroll_run_id": payroll_run_id,
        "summary": result["totals"],
    }
