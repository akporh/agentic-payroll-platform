"""
End-to-end integration test: partial payroll run.

Validates that the payroll engine continues processing all employees
even when one employee's calculation fails, producing a mixed result
set with both SUCCESS and FAILED entries.

Failure injection
-----------------
Employee B is given a salary_definition whose components_jsonb contains
a non-numeric amount: {"BASIC": {"amount": "INVALID"}}.

The payroll route maps this to {"code": "BASIC", "amount": "INVALID"}.
Inside execute_single_employee_payroll → calculate_gross(), the call
Decimal("INVALID") raises decimal.InvalidOperation.

batch_processor.py catches the exception (execution_mode="isolated"),
records status=FAILED with an error_message, and continues to the
next employee.

run_executor.py detects failure_count > 0 and sets the payroll_run
status to PARTIAL instead of CALCULATED.

Requirements
------------
- PostgreSQL running at DATABASE_URL env var.
- All Alembic migrations applied, including:
    d5e6f7a8b9c0_make_employee_contract_grade_nullable
- Pre-existing tax_band rows are harmless: /payroll/run filters by
  the highest-version statutory_rule (ORDER BY version DESC LIMIT 1).
  This test inserts a statutory_rule with version=9998 so it wins
  when the existing pipeline test (version=9999) is not present.

Run:
    pytest tests/test_payroll_partial_run_e2e.py -v
"""

import uuid
from decimal import Decimal

from fastapi.testclient import TestClient
from psycopg2.extras import Json
from sqlalchemy import text

from backend.api.main import app
from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal

client = TestClient(app)

# ---------------------------------------------------------------------------
# Salary components for Employee A (valid)
# ---------------------------------------------------------------------------
BASIC     = 500_000
HOUSING   = 200_000
TRANSPORT = 100_000
GROSS     = BASIC + HOUSING + TRANSPORT   # 800_000

# Expected PAYE using seeded 5-band rates + 8% explicit pension. No NHF workspace rule
# is configured so NHF is not deducted.
#   Pension = GROSS × 8% = 64 000
#   Annual taxable = (800k - 64k) × 12 = 8 832 000
#   Band 1  0–300k       @ 7%  →    21 000
#   Band 2  300k–600k    @ 11% →    33 000
#   Band 3  600k–1100k   @ 15% →    75 000
#   Band 4  1100k–1600k  @ 19% →    95 000
#   Band 5  1600k+       @ 21% → 1 518 720
#   Monthly PAYE = 1 742 720 / 12 = 145 226.67
#   NET = 800 000 - 64 000 - 145 226.67 = 590 773.33
EXPECTED_PAYE = 145_226.67
EXPECTED_NET  = 590_773.33


def test_partial_payroll_run_e2e():
    """
    Prove that a partial payroll run records both SUCCESS and FAILED results.

    Employee A → valid salary_definition → SUCCESS with correct net pay.
    Employee B → invalid amount ("INVALID") → FAILED with error_message.

    The payroll run must:
    - not crash (API returns 200)
    - report success_count=1, failure_count=1
    - persist payroll_run with status=PARTIAL
    - persist two payroll_result rows: one SUCCESS, one FAILED
    """

    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()
    broken_sal_def_id     = uuid.uuid4()
    employee_b_id         = uuid.uuid4()

    db = SessionLocal()

    try:
        # -------------------------------------------------------------------
        # STEP 1 — Insert prerequisites
        # -------------------------------------------------------------------

        # 1a. Account
        db.add(Account(
            account_id=account_id,
            name="Partial Run Test Corp",
        ))

        # 1b. Workspace — starts DRAFT; activated to LIVE before payroll run
        db.add(Workspace(
            workspace_id=workspace_id,
            account_id=account_id,
            name="Partial Run Test Workspace",
            country_code="NG",
            base_currency="NGN",
            status="DRAFT",
        ))

        # 1c. Statutory rule — version=9998 so it wins ORDER BY version DESC
        #     when the full-pipeline test (version=9999) is not in the DB
        db.execute(
            text("""
                INSERT INTO statutory_rule
                    (statutory_rule_id, state, version, rules_jsonb, country_code, effective_from)
                VALUES (:id, 'NATIONAL', 9998, '{"pension": {"employee_rate": 0.08, "employer_rate": 0.10}}', 'NG', '2026-03-01')
            """),
            {"id": statutory_rule_id},
        )

        # 1d. Tax bands — scoped to this statutory_rule_id; same brackets as
        #     the full-pipeline test so Expected PAYE = 84 000 applies
        tax_bands = [
            (0,         300_000,   0.07),
            (300_000,   600_000,   0.11),
            (600_000,   1_100_000, 0.15),
            (1_100_000, 1_600_000, 0.19),
            (1_600_000, None,      0.21),
        ]
        for lower, upper, rate in tax_bands:
            db.execute(
                text("""
                    INSERT INTO tax_band
                        (tax_band_id, statutory_rule_id, lower_limit, upper_limit, rate)
                    VALUES
                        (gen_random_uuid(), :sr_id, :lower, :upper, :rate)
                """),
                {"sr_id": statutory_rule_id, "lower": lower, "upper": upper, "rate": rate},
            )

        # 1e. Component metadata — required by trg_enforce_payroll_readiness
        db.execute(
            text("""
                INSERT INTO component_metadata
                    (component_metadata_id, component_code, country_code, version,
                     metadata_json, effective_from, is_active)
                VALUES (:cm_id, 'TEST_SEED', 'NG', 9998, '{}', CURRENT_DATE, true)
            """),
            {"cm_id": component_metadata_id},
        )

        db.commit()

        # -------------------------------------------------------------------
        # STEP 2 — Onboard Employee A via the commit endpoint
        #
        # Employee A receives a valid STANDARD salary_definition.
        # The commit endpoint handles INSERT for salary_definition,
        # payroll_rule, employee, and employee_contract.
        # -------------------------------------------------------------------
        onboarding_payload = {
            "workspace_id": str(workspace_id),
            "salary_definitions": [
                {
                    "name": "STANDARD",
                    "components": {
                        "BASIC":     {"amount": BASIC},
                        "HOUSING":   {"amount": HOUSING},
                        "TRANSPORT": {"amount": TRANSPORT},
                    },
                }
            ],
            "payroll_rules": [
                {
                    "rule_code": "PENSION",
                    "rule_name": "Employee Pension",
                    "definition": {
                        "method":          "percentage",
                        "rate":            0.08,
                        "base_components": ["BASIC", "HOUSING", "TRANSPORT"],
                    },
                }
            ],
            "employees": [
                {
                    "employee_number":        "EMP001",
                    "full_name":              "Jane Okeke",
                    "salary_definition_name": "STANDARD",
                    "contract_start":         "2025-01-01",
                    "biodata": {
                        "TIN":            "1234567890",
                        "BANK":           "GTBank",
                        "ACCOUNT_NUMBER": "0123456789",
                        "RSA":            "PEN100123456",
                        "FULL_NAME":      "Jane Okeke",
                    },
                }
            ],
        }

        commit_resp = client.post("/api/v1/onboarding/commit", json=onboarding_payload)
        assert commit_resp.status_code == 200, (
            f"Commit HTTP status: {commit_resp.status_code}\n{commit_resp.text}"
        )
        commit_body = commit_resp.json()
        assert commit_body["status"] == "success", f"Commit failed: {commit_body}"

        # -------------------------------------------------------------------
        # STEP 3 — Verify Employee A was persisted
        # -------------------------------------------------------------------
        emp_a_row = db.execute(
            text("""
                SELECT employee_id, full_name, status
                FROM employee
                WHERE workspace_id = :wid
            """),
            {"wid": workspace_id},
        ).fetchone()

        assert emp_a_row is not None, "Employee A not found in DB after commit"
        employee_a_id = emp_a_row[0]
        assert emp_a_row[1] == "Jane Okeke"
        assert emp_a_row[2] == "ACTIVE"

        # -------------------------------------------------------------------
        # STEP 4 — Insert Employee B with a deliberately broken salary_definition
        #
        # components_jsonb stores "INVALID" as the amount string.
        # The payroll route reads: {"code": "BASIC", "amount": "INVALID"}.
        # Inside calculate_gross(), Decimal("INVALID") raises
        # decimal.InvalidOperation.  batch_processor.py catches this and
        # records status=FAILED — the run continues for Employee A.
        # -------------------------------------------------------------------
        db.execute(
            text("""
                INSERT INTO salary_definition (
                    salary_definition_id, workspace_id, name, code, components_jsonb
                )
                VALUES (:id, :wid, 'BROKEN', 'BROKEN', :components)
            """),
            {
                "id":         broken_sal_def_id,
                "wid":        workspace_id,
                "components": Json({"BASIC": {"amount": "INVALID"}}),
            },
        )

        db.execute(
            text("""
                INSERT INTO employee (employee_id, workspace_id, full_name, status)
                VALUES (:eid, :wid, 'Broken Employee', 'ACTIVE')
            """),
            {"eid": employee_b_id, "wid": workspace_id},
        )

        db.execute(
            text("""
                INSERT INTO employee_contract (
                    contract_id, employee_id, salary_definition_id, start_date
                )
                VALUES (gen_random_uuid(), :eid, :sdid, '2025-01-01')
            """),
            {"eid": employee_b_id, "sdid": broken_sal_def_id},
        )

        db.commit()

        # -------------------------------------------------------------------
        # STEP 5 — Activate workspace
        #
        # DB trigger trg_enforce_workspace_live (migration 0daab4ac893b)
        # blocks any INSERT on payroll_run unless workspace.status = 'LIVE'.
        # -------------------------------------------------------------------
        db.execute(
            text("UPDATE workspace SET status = 'LIVE' WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )
        db.commit()

        ws_status = db.execute(
            text("SELECT status FROM workspace WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).scalar()
        assert ws_status == "LIVE", f"Workspace status not LIVE: {ws_status}"

        # -------------------------------------------------------------------
        # STEP 6 — Run payroll
        #
        # POST /api/v1/payroll/run with execution_mode="isolated" (default).
        # Both employees are loaded. Employee A succeeds; Employee B fails.
        # -------------------------------------------------------------------
        payroll_resp = client.post(
            "/api/v1/payroll/run",
            json={"workspace_id": str(workspace_id)},
        )

        assert payroll_resp.status_code == 200, (
            f"Payroll HTTP status: {payroll_resp.status_code}\n{payroll_resp.text}"
        )
        payroll_body = payroll_resp.json()
        assert payroll_body["status"] == "success", (
            f"Payroll run failed: {payroll_body}"
        )

        payroll_run_id = payroll_body["payroll_run_id"]
        assert payroll_run_id is not None

        # -------------------------------------------------------------------
        # STEP 7 — Validate summary counts
        # -------------------------------------------------------------------
        summary = payroll_body["summary"]
        assert summary["success_count"] == 1, (
            f"Expected 1 success, got: {summary}"
        )
        assert summary["failure_count"] == 1, (
            f"Expected 1 failure, got: {summary}"
        )

        # Totals reflect only the successful employee
        assert float(summary["total_gross_pay"]) == float(GROSS), (
            f"total_gross_pay mismatch: {summary}"
        )
        assert float(summary["total_net_pay"]) == float(EXPECTED_NET), (
            f"total_net_pay mismatch: {summary}"
        )

        # -------------------------------------------------------------------
        # STEP 8 — Verify payroll_run status is PARTIAL
        #
        # run_executor.py: failure_count > 0 → CALCULATING → PARTIAL
        # -------------------------------------------------------------------
        run_row = db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :run_id"),
            {"run_id": payroll_run_id},
        ).fetchone()

        assert run_row is not None, "payroll_run row not found in DB"
        assert run_row[0] == "PARTIAL", (
            f"Expected payroll_run status PARTIAL, got {run_row[0]}"
        )

        # -------------------------------------------------------------------
        # STEP 9 — Verify both payroll_result rows are persisted
        # -------------------------------------------------------------------
        result_rows = db.execute(
            text("""
                SELECT employee_id, status, net_pay, error_message
                FROM payroll_result
                WHERE payroll_run_id = :run_id
            """),
            {"run_id": payroll_run_id},
        ).fetchall()

        assert len(result_rows) == 2, (
            f"Expected 2 payroll_result rows, got {len(result_rows)}"
        )

        results_by_employee = {str(r[0]): r for r in result_rows}

        assert str(employee_a_id) in results_by_employee, (
            "Employee A result not found in payroll_result"
        )
        assert str(employee_b_id) in results_by_employee, (
            "Employee B result not found in payroll_result"
        )

        # Employee A — SUCCESS with correct net pay
        a_result = results_by_employee[str(employee_a_id)]
        assert a_result[1] == "SUCCESS", (
            f"Employee A: expected SUCCESS, got {a_result[1]}"
        )
        assert float(a_result[2]) == float(EXPECTED_NET), (
            f"Employee A net_pay: expected {EXPECTED_NET}, got {a_result[2]}"
        )
        assert a_result[3] is None, (
            f"Employee A should have no error_message, got: {a_result[3]}"
        )

        # Employee B — FAILED with a non-empty error message
        b_result = results_by_employee[str(employee_b_id)]
        assert b_result[1] == "FAILED", (
            f"Employee B: expected FAILED, got {b_result[1]}"
        )
        assert b_result[3] is not None, (
            "Employee B must have a non-null error_message"
        )
        assert len(b_result[3]) > 0, (
            "Employee B error_message must not be empty"
        )

    finally:
        # -------------------------------------------------------------------
        # Cleanup — delete in reverse FK dependency order.
        # Each statement is scoped to this test's workspace/IDs only.
        # -------------------------------------------------------------------

        # Roll back any in-progress transaction before starting cleanup
        # (the test may have failed mid-way, leaving the session in an aborted
        # transaction state which would cause SET LOCAL to fail).
        db.rollback()

        # Bypass immutability triggers so cleanup succeeds at any lifecycle state
        db.execute(text("SET LOCAL session_replication_role = replica"))

        db.execute(
            text("""
                DELETE FROM payroll_result
                WHERE payroll_run_id IN (
                    SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid
                )
            """),
            {"wid": workspace_id},
        )

        db.execute(
            text("""
                DELETE FROM event_store
                WHERE aggregate_type = 'PAYROLL_RUN'
                  AND aggregate_id IN (
                    SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid
                  )
            """),
            {"wid": workspace_id},
        )

        db.execute(
            text("DELETE FROM audit_log WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )

        db.execute(
            text("DELETE FROM payroll_run WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )

        db.execute(
            text("""
                DELETE FROM employee_contract
                WHERE employee_id IN (
                    SELECT employee_id FROM employee WHERE workspace_id = :wid
                )
            """),
            {"wid": workspace_id},
        )

        db.execute(
            text("DELETE FROM employee WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )

        db.execute(
            text("DELETE FROM payroll_rule WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )

        db.execute(
            text("DELETE FROM salary_definition WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )

        db.execute(
            text("DELETE FROM tax_band WHERE statutory_rule_id = :sr_id"),
            {"sr_id": statutory_rule_id},
        )

        db.execute(
            text("DELETE FROM statutory_rule WHERE statutory_rule_id = :sr_id"),
            {"sr_id": statutory_rule_id},
        )

        db.execute(
            text("""
                DELETE FROM component_metadata
                WHERE component_metadata_id = :cm_id
            """),
            {"cm_id": component_metadata_id},
        )

        db.execute(
            text("DELETE FROM workspace WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )

        db.execute(
            text("DELETE FROM account WHERE account_id = :aid"),
            {"aid": account_id},
        )

        db.commit()
        db.close()
