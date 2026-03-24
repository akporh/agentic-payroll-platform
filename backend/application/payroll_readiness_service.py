"""
Payroll Run Readiness Validator.

Checks all pre-flight conditions required before a payroll run can be
executed.  This is a Python application-layer check; the DB trigger
trg_enforce_payroll_readiness (migration 4907cf6eb08f) enforces a
complementary set of conditions (workspace status, statutory rules, tax
bands, component metadata) at INSERT time.

Conditions checked here
-----------------------
1. Payroll run exists and is associated with a known workspace.
2. Payroll run status is DRAFT.
3. Pay period (period_start, period_end) is set and coherent.
4. No payroll_result rows already exist for this run.
5. At least one active employee with an active contract exists in the
   workspace.
6. Every active employee has a salary_definition via employee_contract.
7. Every salary_definition has at least one pay component.
8. Every pay component has a valid numeric amount.
   (Adapted from "all pay components exist in pay_component table" —
   this schema stores components as JSONB within salary_definition;
   structural validity is enforced here instead of a table lookup.)
"""

from decimal import Decimal, InvalidOperation

from sqlalchemy import text

from backend.infra.db.session import SessionLocal


def validate_payroll_run_ready(run_id: str) -> dict:
    """Validate that a payroll run is ready to be executed.

    Args:
        run_id: The payroll_run_id to validate.

    Returns:
        {
            "ready": bool,
            "errors": list[str],   # empty when ready=True
        }
    """
    errors = []
    db = SessionLocal()

    try:
        # -------------------------------------------------------------------
        # 1. Run must exist — load workspace_id, status, and pay period.
        # -------------------------------------------------------------------
        run_row = db.execute(
            text("""
                SELECT workspace_id, status, period_start, period_end
                FROM   payroll_run
                WHERE  payroll_run_id = :rid
            """),
            {"rid": run_id},
        ).fetchone()

        if run_row is None:
            return {"ready": False, "errors": [f"Payroll run not found: {run_id}"]}

        workspace_id = str(run_row[0])
        status       = run_row[1]
        period_start = run_row[2]
        period_end   = run_row[3]

        # -------------------------------------------------------------------
        # 2. Status must be DRAFT.
        # -------------------------------------------------------------------
        if status != "DRAFT":
            errors.append(
                f"Payroll run status must be DRAFT; current status: {status}"
            )

        # -------------------------------------------------------------------
        # 3. Pay period must be set and coherent.
        # -------------------------------------------------------------------
        if period_start is None or period_end is None:
            errors.append("Pay period (period_start, period_end) is not set")
        elif period_end < period_start:
            errors.append(
                "Pay period end date must not be before period start date"
            )
        elif (period_end - period_start).days + 1 > 366:
            errors.append(
                f"Pay period span of {(period_end - period_start).days + 1} days "
                "exceeds the maximum allowed (366). Check period_start and period_end."
            )

        # -------------------------------------------------------------------
        # 4. No existing payroll_result rows for this run.
        # -------------------------------------------------------------------
        result_count = db.execute(
            text("""
                SELECT COUNT(*)
                FROM   payroll_result
                WHERE  payroll_run_id = :rid
            """),
            {"rid": run_id},
        ).scalar()

        if result_count > 0:
            errors.append(
                f"Payroll run already has {result_count} result(s); "
                "cannot execute a run that already has results"
            )

        # -------------------------------------------------------------------
        # 5–8. Employee, salary definition, and component checks.
        # -------------------------------------------------------------------
        employee_rows = db.execute(
            text("""
                SELECT
                    e.employee_id,
                    e.full_name,
                    ec.salary_definition_id
                FROM   employee e
                LEFT   JOIN employee_contract ec
                           ON  e.employee_id = ec.employee_id
                           AND (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
                WHERE  e.workspace_id = :wid
                  AND  e.status       = 'ACTIVE'
            """),
            {"wid": workspace_id},
        ).fetchall()

        if not employee_rows:
            errors.append("No active employees found in workspace")
        else:
            for emp_id, emp_name, salary_def_id in employee_rows:

                # 6. Each active employee must have a salary_definition link.
                if salary_def_id is None:
                    errors.append(
                        f"Employee '{emp_name}' is missing a salary definition"
                    )
                    continue

                # Load the salary definition.
                sal_row = db.execute(
                    text("""
                        SELECT components_jsonb
                        FROM   salary_definition
                        WHERE  salary_definition_id = :sid
                    """),
                    {"sid": salary_def_id},
                ).fetchone()

                if sal_row is None:
                    errors.append(
                        f"Employee '{emp_name}' references a "
                        "non-existent salary definition"
                    )
                    continue

                components = sal_row[0]

                # 7. Salary definition must have at least one component.
                if not components:
                    errors.append(
                        f"Employee '{emp_name}' has a salary definition "
                        "with no pay components"
                    )
                    continue

                # 8. Each component must have a valid numeric amount.
                #    (Adapted from "pay_component table" check — no such
                #    table in this schema; structural validity is used.)
                for code, defn in components.items():
                    if not isinstance(defn, dict) or "amount" not in defn:
                        errors.append(
                            f"Pay component '{code}' for employee "
                            f"'{emp_name}' is missing the required "
                            "'amount' field"
                        )
                        continue
                    try:
                        Decimal(str(defn["amount"]))
                    except InvalidOperation:
                        errors.append(
                            f"Pay component '{code}' for employee "
                            f"'{emp_name}' has a non-numeric amount: "
                            f"{defn['amount']!r}"
                        )

        return {"ready": len(errors) == 0, "errors": errors}

    finally:
        db.close()
