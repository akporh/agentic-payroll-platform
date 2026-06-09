import json
import uuid
from sqlalchemy import text
from backend.infra.db import get_session


def load_employee_contracts(workspace_id: str, path: str):
    """
    Phase 1: Assign employees to grades + salary definitions via contracts.
    """

    with open(path) as f:
        contracts = json.load(f)

    db = get_session()

    for c in contracts:

        # Lookup employee_id
        emp = db.execute(
            text("SELECT employee_id FROM employee WHERE employee_number = :num"),
            {"num": c["employee_number"]},
        ).fetchone()

        if not emp:
            raise Exception(f"Employee not found: {c['employee_number']}")

        # Lookup grade_id
        grade = db.execute(
            text("SELECT grade_id FROM grade WHERE grade_code = :code AND workspace_id = :ws"),
            {"code": c["grade_code"], "ws": workspace_id},
        ).fetchone()

        if not grade:
            raise Exception(f"Grade not found: {c['grade_code']}")

        # Lookup salary_definition_id
        sal = db.execute(
            text("SELECT salary_definition_id FROM salary_definition WHERE name = :name"),
            {"name": c["salary_definition_name"]},
        ).fetchone()

        if not sal:
            raise Exception(f"Salary definition not found: {c['salary_definition_name']}")

        # Insert contract
        db.execute(
            text("""
            INSERT INTO employee_contract (
                contract_id,
                employee_id,
                salary_definition_id,
                grade_id,
                start_date,
                end_date,
                change_reason,
                imported_grade_label,
                imported_designation_label
            )
            VALUES (
                :id,
                :emp,
                :sal,
                :grade,
                :start,
                NULL,
                'Initial ACME load',
                NULL,
                NULL
            )
            """),
            {
                "id": str(uuid.uuid4()),
                "emp": emp.employee_id,
                "sal": sal.salary_definition_id,
                "grade": grade.grade_id,
                "start": c["start_date"],
            },
        )

    db.commit()
    print("Loaded employee contracts successfully.")


if __name__ == "__main__":
    load_employee_contracts(
        workspace_id="6b70612c-b2e1-4275-800c-33140e7f4ebd",
        path="data/acme_contracts.json",
    )

