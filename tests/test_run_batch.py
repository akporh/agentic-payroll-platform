import uuid
from datetime import date
import json

from backend.infra.db.session import SessionLocal
from backend.application.payroll_run_service import execute_and_persist
from sqlalchemy import text

def main():
    db = SessionLocal()

    # ---- Load Workspace ----
    workspace_id = db.execute(
        text("SELECT workspace_id FROM workspace LIMIT 1")
    ).scalar()

    if not workspace_id:
        raise Exception("No workspace found")

    # ---- Load Employees ----
    employees = []
    query = text("""
    SELECT e.employee_id, sd.components_jsonb
    FROM employee e
    JOIN employee_contract ec
      ON e.employee_id = ec.employee_id
    JOIN salary_definition sd
      ON ec.salary_definition_id = sd.salary_definition_id
    WHERE e.workspace_id = :workspace_id
      AND e.status = 'ACTIVE'
      AND (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
    """)
      # Execute and fetch
    result = db.execute(query,{"workspace_id": workspace_id})
    rows = result.fetchall()

    for row in rows:
        employees.append({
            "employee_id": str(row[0]),
            "components": [
                {"code": k, "amount": v["amount"]}
                for k, v in row[1].items()
            ],
        })

    # ---- Load Tax Bands ----
    tax_rows = db.execute(text("""
        SELECT lower_limit, upper_limit, rate
        FROM tax_band
        ORDER BY lower_limit
    """)).fetchall()

    tax_bands = [
        {
            "lower_limit": r[0],
            "upper_limit": r[1],
            "rate": r[2],
        }
        for r in tax_rows
    ]

    # ---- Load Statutory Rule ----
    stat_row = db.execute(text("""
        SELECT statutory_rule_id, version
        FROM statutory_rule
        ORDER BY version DESC
        LIMIT 1
    """)).fetchone()

    statutory_rule_id = str(stat_row[0])
    statutory_version = stat_row[1]

    # ---- Load Payroll Rules ----
    rule_rows = db.execute(text("""
        SELECT rule_id
        FROM payroll_rule
        WHERE is_active = TRUE
    """)).fetchall()

    payroll_rule_ids = [str(r[0]) for r in rule_rows]

    print("🚀 Running batch payroll...")

    result = execute_and_persist(
        payroll_run_id=str(uuid.uuid4()),
        workspace_id=str(workspace_id),
        employees=employees,
        tax_bands=tax_bands,
        statutory_rule_id=statutory_rule_id,
        statutory_version=statutory_version,
        payroll_rule_ids=payroll_rule_ids,
        performed_by="admin@test.com",
        execution_mode="isolated",  # change to "atomic" to test atomic mode
    )

    print("✅ Batch Completed")
    print(json.dumps(result, indent=2, default=str))

    db.close()


if __name__ == "__main__":
    main()
