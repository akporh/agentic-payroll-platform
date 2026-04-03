"""
End-to-end integration test: payroll retry.

Validates the full retry lifecycle:

  Phase 1 — Initial run (PARTIAL)
  --------------------------------
  Two employees are onboarded.  Employee B has a broken salary_definition
  (amount = "INVALID"), which causes decimal.InvalidOperation inside
  calculate_gross().  The batch processor captures the failure and the
  run ends with status=PARTIAL.

    Employee A  →  SUCCESS  (net_pay = 578 273.33)
    Employee B  →  FAILED   (error_message non-empty)

  Phase 2 — Fix data + retry
  ---------------------------
  Employee B's salary_definition is corrected via a direct UPDATE.
  The retry endpoint is called.  The service re-runs calculation using
  the corrected components, replaces the FAILED result row with a SUCCESS
  row, and transitions the run to CALCULATED.

    Employee A  →  unchanged SUCCESS
    Employee B  →  SUCCESS after retry  (net_pay = 292 553.33)
    payroll_run →  status = CALCULATED

  Idempotency check
  -----------------
  A second retry call on the same run (now CALCULATED) must return 400
  because only PARTIAL runs are retryable.

Requirements
------------
- PostgreSQL running at DATABASE_URL env var.
- All Alembic migrations applied, including:
    d5e6f7a8b9c0_make_employee_contract_grade_nullable
- This test uses statutory_rule version=9997 so it wins ORDER BY version DESC
  when the pipeline test (9999) and the partial-run test (9998) are absent.

Run:
    pytest tests/test_payroll_retry.py -v
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
# Employee A — valid salary
# ---------------------------------------------------------------------------
BASIC_A     = 500_000
HOUSING_A   = 200_000
TRANSPORT_A = 100_000
GROSS_A     = BASIC_A + HOUSING_A + TRANSPORT_A   # 800_000

# 5-band PAYE + 8% explicit pension (rules_jsonb pension.employee_rate=0.08) + 2.5% NHF:
#   Pension_A = 800k × 8% = 64 000;  NHF_A = 500k × 2.5% = 12 500
#   Annual taxable_A = (800k - 64k) × 12 = 8 832 000 → Monthly PAYE = 145 226.67
#   NET_A = 800 000 - 64 000 - 145 226.67 - 12 500 = 578 273.33
EXPECTED_PAYE_A = 145_226.67
EXPECTED_NET_A  = 578_273.33

# ---------------------------------------------------------------------------
# Employee B — fixed salary (after correction)
# ---------------------------------------------------------------------------
BASIC_B   = 300_000
HOUSING_B = 100_000
GROSS_B   = BASIC_B + HOUSING_B   # 400_000

# 5-band PAYE + 8% explicit pension + 2.5% NHF (no TRANSPORT for B):
#   Pension_B = 400k × 8% = 32 000;  NHF_B = 300k × 2.5% = 7 500
#   Annual taxable_B = (400k - 32k) × 12 = 4 416 000
#   → Monthly PAYE = 815 360 / 12 = 67 946.67
#   NET_B = 400 000 - 32 000 - 67 946.67 - 7 500 = 292 553.33
EXPECTED_PAYE_B = 67_946.67
EXPECTED_NET_B  = 292_553.33


def test_payroll_retry_e2e():
    """
    Full retry lifecycle:
    1. Run payroll with Employee A (valid) + Employee B (broken) → PARTIAL
    2. Fix Employee B's salary data
    3. Call retry endpoint → CALCULATED
    4. Assert Employee A unchanged, Employee B now SUCCESS
    5. Assert second retry call returns 400 (run is no longer PARTIAL)
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

        db.add(Account(
            account_id=account_id,
            name="Retry Test Corp",
        ))

        db.add(Workspace(
            workspace_id=workspace_id,
            account_id=account_id,
            name="Retry Test Workspace",
            country_code="NG",
            base_currency="NGN",
            status="DRAFT",
        ))

        # version=9997 wins when the pipeline (9999) and partial (9998) tests
        # are not running concurrently
        db.execute(
            text("""
                INSERT INTO statutory_rule
                    (statutory_rule_id, state, version, rules_jsonb, country_code, effective_from)
                VALUES (:id, 'NATIONAL', 9997, '{"pension": {"employee_rate": 0.08, "employer_rate": 0.10}}', 'NG', '2000-01-01')
            """),
            {"id": statutory_rule_id},
        )

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

        db.execute(
            text("""
                INSERT INTO component_metadata
                    (component_metadata_id, component_code, country_code, version,
                     metadata_json, effective_from, is_active)
                VALUES (:cm_id, 'TEST_SEED', 'NG', 9997, '{}', CURRENT_DATE, true)
            """),
            {"cm_id": component_metadata_id},
        )

        db.commit()

        # -------------------------------------------------------------------
        # STEP 2 — Onboard Employee A via commit endpoint
        # -------------------------------------------------------------------
        onboarding_payload = {
            "workspace_id": str(workspace_id),
            "salary_definitions": [
                {
                    "name": "STANDARD",
                    "components": {
                        "BASIC":     {"amount": BASIC_A},
                        "HOUSING":   {"amount": HOUSING_A},
                        "TRANSPORT": {"amount": TRANSPORT_A},
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
            f"Commit HTTP {commit_resp.status_code}: {commit_resp.text}"
        )
        assert commit_resp.json()["status"] == "success"

        # Capture Employee A's id for later assertions
        emp_a_row = db.execute(
            text("SELECT employee_id FROM employee WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).fetchone()
        assert emp_a_row is not None
        employee_a_id = emp_a_row[0]

        # -------------------------------------------------------------------
        # STEP 3 — Insert Employee B with broken salary data directly
        #
        # components_jsonb stores amount = "INVALID".
        # calculate_gross() does Decimal("INVALID") → InvalidOperation.
        # batch_processor catches this → FAILED result, run continues.
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
        # STEP 4 — Activate workspace
        # -------------------------------------------------------------------
        db.execute(
            text("UPDATE workspace SET status = 'LIVE' WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )
        db.commit()

        assert db.execute(
            text("SELECT status FROM workspace WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).scalar() == "LIVE"

        # -------------------------------------------------------------------
        # STEP 5 — Phase 1: run payroll → expect PARTIAL
        # -------------------------------------------------------------------
        payroll_resp = client.post(
            "/api/v1/payroll/run",
            json={"workspace_id": str(workspace_id)},
        )

        assert payroll_resp.status_code == 200, (
            f"Payroll HTTP {payroll_resp.status_code}: {payroll_resp.text}"
        )
        payroll_body = payroll_resp.json()
        assert payroll_body["status"] == "success", payroll_body

        payroll_run_id = payroll_body["payroll_run_id"]

        summary = payroll_body["summary"]
        assert summary["success_count"] == 1, f"Expected 1 success: {summary}"
        assert summary["failure_count"] == 1, f"Expected 1 failure: {summary}"

        # payroll_run.status must be PARTIAL
        run_status = db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": payroll_run_id},
        ).scalar()
        assert run_status == "PARTIAL", f"Expected PARTIAL, got {run_status}"

        # Confirm per-employee results before retry
        def fetch_results():
            rows = db.execute(
                text("""
                    SELECT employee_id, status, net_pay, error_message
                    FROM payroll_result
                    WHERE payroll_run_id = :rid
                """),
                {"rid": payroll_run_id},
            ).fetchall()
            return {str(r[0]): r for r in rows}

        pre_retry = fetch_results()
        assert pre_retry[str(employee_a_id)][1] == "SUCCESS"
        assert pre_retry[str(employee_b_id)][1] == "FAILED"
        assert pre_retry[str(employee_b_id)][3] is not None   # has error

        # -------------------------------------------------------------------
        # STEP 6 — Fix Employee B's salary definition
        #
        # Replace "INVALID" with a valid numeric amount.
        # The retry service loads the CURRENT components from the DB, so it
        # picks up this correction automatically.
        # -------------------------------------------------------------------
        db.execute(
            text("""
                UPDATE salary_definition
                SET    components_jsonb = :components
                WHERE  salary_definition_id = :id
            """),
            {
                "components": Json({
                    "BASIC":   {"amount": BASIC_B},
                    "HOUSING": {"amount": HOUSING_B},
                }),
                "id": broken_sal_def_id,
            },
        )
        db.commit()

        # -------------------------------------------------------------------
        # STEP 7 — Phase 2: call the retry endpoint
        # -------------------------------------------------------------------
        retry_resp = client.post(f"/api/v1/payroll/run/{payroll_run_id}/retry")

        assert retry_resp.status_code == 200, (
            f"Retry HTTP {retry_resp.status_code}: {retry_resp.text}"
        )
        retry_body = retry_resp.json()
        assert retry_body["status"] == "success", retry_body
        assert retry_body["retried"]      == 1, f"Expected 1 retried: {retry_body}"
        assert retry_body["success"]      == 1, f"Expected 1 success: {retry_body}"
        assert retry_body["still_failed"] == 0, f"Expected 0 still_failed: {retry_body}"

        # -------------------------------------------------------------------
        # STEP 8 — Verify payroll_run status is now CALCULATED
        # -------------------------------------------------------------------
        run_status_after = db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": payroll_run_id},
        ).scalar()
        assert run_status_after == "CALCULATED", (
            f"Expected CALCULATED after retry, got {run_status_after}"
        )

        # -------------------------------------------------------------------
        # STEP 9 — Verify per-employee results after retry
        # -------------------------------------------------------------------
        post_retry = fetch_results()

        assert len(post_retry) == 2, (
            f"Expected 2 payroll_result rows, got {len(post_retry)}"
        )

        # Employee A — unchanged SUCCESS with correct net pay
        a = post_retry[str(employee_a_id)]
        assert a[1] == "SUCCESS", f"Employee A: expected SUCCESS, got {a[1]}"
        assert float(a[2]) == float(EXPECTED_NET_A), (
            f"Employee A net_pay: expected {EXPECTED_NET_A}, got {a[2]}"
        )
        assert a[3] is None, f"Employee A must have no error, got: {a[3]}"

        # Employee B — now SUCCESS with the corrected salary
        b = post_retry[str(employee_b_id)]
        assert b[1] == "SUCCESS", f"Employee B: expected SUCCESS after retry, got {b[1]}"
        assert float(b[2]) == float(EXPECTED_NET_B), (
            f"Employee B net_pay: expected {EXPECTED_NET_B}, got {b[2]}"
        )
        assert b[3] is None, f"Employee B must have no error after retry, got: {b[3]}"

        # -------------------------------------------------------------------
        # STEP 10 — Idempotency: second retry on a CALCULATED run returns 400
        # -------------------------------------------------------------------
        second_retry = client.post(f"/api/v1/payroll/run/{payroll_run_id}/retry")
        assert second_retry.status_code == 400, (
            f"Expected 400 for retry on CALCULATED run, got {second_retry.status_code}"
        )

    finally:
        # -------------------------------------------------------------------
        # Cleanup — reverse FK order; scoped to this test's IDs only
        # -------------------------------------------------------------------
        db.rollback()
        # Bypass immutability triggers so teardown succeeds at any lifecycle state.
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
            text("DELETE FROM component_metadata WHERE component_metadata_id = :cm_id"),
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
