"""
End-to-end integration test: full payroll pipeline.

Validates the complete vertical flow:
    Onboarding Upload
    → Onboarding Commit
    → Employees Persisted
    → Payroll Run
    → Payroll Results Persisted
    → Correct Totals Returned

Requirements
------------
- PostgreSQL running at DATABASE_URL env var.
- All Alembic migrations applied, including:
    d5e6f7a8b9c0_make_employee_contract_grade_nullable
  Without that migration, employee_contract.grade_id is NOT NULL and
  the commit endpoint's INSERT will fail.
- Pre-existing tax_band rows are harmless: /payroll/run filters bands by
  the statutory_rule_id selected via ORDER BY version DESC LIMIT 1.
  This test inserts a statutory_rule with version=9999 so it always wins,
  and its dedicated tax bands are the only ones used in the calculation.

Run:
    pytest tests/test_payroll_pipeline_e2e.py -v
"""

import uuid
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.api.main import app
from backend.infra.db.session import SessionLocal
from backend.infra.db.models import Account, Workspace

client = TestClient(app)

# ---------------------------------------------------------------------------
# Salary components used throughout the test
# ---------------------------------------------------------------------------
BASIC     = 500_000
HOUSING   = 200_000
TRANSPORT = 100_000
GROSS     = BASIC + HOUSING + TRANSPORT   # 800_000

# Expected values using 5 bands seeded below + explicit pension rates in rules_jsonb:
# (pension.employee_rate=8%, nhf=2.5%):
#
#   Pension employee  = GROSS × 8%          =  64 000
#   NHF               = BASIC × 2.5%        =  12 500
#   Annual taxable    = (800k - 64k) × 12   = 8 832 000
#   Band 1  0–300k       @ 7%  →    21 000
#   Band 2  300k–600k    @ 11% →    33 000
#   Band 3  600k–1100k   @ 15% →    75 000
#   Band 4  1100k–1600k  @ 19% →    95 000
#   Band 5  1600k+       @ 21% → 1 518 720  (7 232 000 × 21%)
#   Annual PAYE           =     1 742 720
#   Monthly PAYE          =       145 226.67
#   NET = 800k - 64k - 145 226.67 - 12 500 = 578 273.33
EXPECTED_PENSION  = 64_000
EXPECTED_NHF      = 12_500
EXPECTED_PAYE     = 145_226.67
EXPECTED_NET      = 578_273.33


def test_full_payroll_pipeline_e2e():
    """Prove the complete payroll pipeline executes and produces correct totals."""

    # -----------------------------------------------------------------------
    # IDs — generated fresh per test run
    # -----------------------------------------------------------------------
    account_id           = uuid.uuid4()
    workspace_id         = uuid.uuid4()
    statutory_rule_id    = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()

    try:
        # -------------------------------------------------------------------
        # STEP 1 — Insert prerequisites
        # -------------------------------------------------------------------

        # 1a. Account
        db.add(Account(
            account_id=account_id,
            name="E2E Test Corp",
        ))

        # 1b. Workspace — status starts as DRAFT; trigger requires LIVE at payroll time
        db.add(Workspace(
            workspace_id=workspace_id,
            account_id=account_id,
            name="E2E Test Workspace",
            country_code="NG",
            base_currency="NGN",
            status="DRAFT",
        ))

        # 1c. Statutory rule — payroll route: SELECT ... JOIN workspace ON country_code
        #     ORDER BY effective_from DESC, version DESC LIMIT 1.
        #     Must include country_code='NG' and effective_from so this rule wins.
        db.execute(
            text("""
                INSERT INTO statutory_rule
                    (statutory_rule_id, state, version, rules_jsonb, country_code, effective_from)
                VALUES (:id, 'NATIONAL', 9999, '{"pension": {"employee_rate": 0.08, "employer_rate": 0.10}}', 'NG', '2000-01-01')
            """),
            {"id": statutory_rule_id},
        )

        # 1d. Tax bands — payroll route filters by statutory_rule_id; our version=9999
        #     rule wins ORDER BY version DESC, so only these bands are used
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
                {
                    "sr_id":  statutory_rule_id,
                    "lower":  lower,
                    "upper":  upper,
                    "rate":   rate,
                },
            )

        # 1e. Component metadata — validate_payroll_readiness checks for an
        #     active record matching workspace.country_code
        db.execute(
            text("""
                INSERT INTO component_metadata
                    (component_metadata_id, component_code, country_code, version,
                     metadata_json, effective_from, is_active)
                VALUES (:cm_id, 'TEST_SEED', 'NG', 9999, '{}', CURRENT_DATE, true)
            """),
            {"cm_id": component_metadata_id},
        )

        db.commit()

        # -------------------------------------------------------------------
        # STEP 2 — Onboarding Upload
        #
        # POST /api/v1/onboarding/upload
        # Validates payload and returns SQL string — no DB writes.
        # workspace_id must be at the ROOT of the payload (flat structure).
        # -------------------------------------------------------------------
        upload_payload = {
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
                    # hard_validator: rule_code must contain "PENSION",
                    # method must be "percentage",
                    # base_components must cover {BASIC, HOUSING, TRANSPORT}
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
                    # full_name used directly by commit INSERT;
                    # biodata.FULL_NAME is the fallback — both provided here
                    "full_name":              "Jane Okeke",
                    "salary_definition_name": "STANDARD",
                    # contract_start before the payroll period to avoid proration
                    "contract_start":         "2025-01-01",
                    "biodata": {
                        # hard_validator requires all four keys in every employee
                        "TIN":            "1234567890",
                        "BANK":           "GTBank",
                        "ACCOUNT_NUMBER": "0123456789",
                        "RSA":            "PEN100123456",
                        "FULL_NAME":      "Jane Okeke",
                    },
                }
            ],
        }

        upload_resp = client.post("/api/v1/onboarding/upload", json=upload_payload)

        assert upload_resp.status_code == 200, (
            f"Upload HTTP status: {upload_resp.status_code}\n{upload_resp.text}"
        )
        upload_body = upload_resp.json()
        assert upload_body["status"] == "success", (
            f"Upload failed: {upload_body}"
        )
        assert "sql" in upload_body, "Upload response must contain sql key"
        assert upload_body["review"]["hard_validation"]["status"] == "PASS", (
            f"Hard validation failed: {upload_body['review']['hard_validation']['errors']}"
        )

        # -------------------------------------------------------------------
        # STEP 3 — Onboarding Commit
        #
        # POST /api/v1/onboarding/commit
        # Re-runs validation, then INSERTs:
        #   salary_definition, payroll_rule, employee, employee_contract
        # Same payload as upload — workspace_id already at root.
        # Requires:
        #   - workspace row in DB (checked by commit endpoint)
        #   - employee_contract.grade_id nullable (migration d5e6f7a8b9c0)
        # -------------------------------------------------------------------
        commit_resp = client.post("/api/v1/onboarding/commit", json=upload_payload)

        assert commit_resp.status_code == 200, (
            f"Commit HTTP status: {commit_resp.status_code}\n{commit_resp.text}"
        )
        commit_body = commit_resp.json()
        assert commit_body["status"] == "success", (
            f"Commit failed: {commit_body}"
        )

        # -------------------------------------------------------------------
        # STEP 4 — Verify persistence
        #
        # Query the DB directly — no endpoint, real session.
        # -------------------------------------------------------------------

        # Employee row
        emp_rows = db.execute(
            text("""
                SELECT employee_id, full_name, status
                FROM employee
                WHERE workspace_id = :wid
            """),
            {"wid": workspace_id},
        ).fetchall()

        assert len(emp_rows) == 1, (
            f"Expected exactly 1 employee, found {len(emp_rows)}"
        )
        employee_id  = emp_rows[0][0]
        employee_name = emp_rows[0][1]
        employee_status = emp_rows[0][2]

        assert employee_name == "Jane Okeke"
        assert employee_status == "ACTIVE"

        # Salary definition row
        sal_def_row = db.execute(
            text("""
                SELECT salary_definition_id, name, components_jsonb
                FROM salary_definition
                WHERE workspace_id = :wid
            """),
            {"wid": workspace_id},
        ).fetchone()

        assert sal_def_row is not None, "salary_definition row missing"
        assert sal_def_row[1] == "STANDARD"

        components = sal_def_row[2]
        assert float(components["BASIC"]["amount"])     == BASIC
        assert float(components["HOUSING"]["amount"])   == HOUSING
        assert float(components["TRANSPORT"]["amount"]) == TRANSPORT

        # Employee contract row — links employee to salary definition
        contract_row = db.execute(
            text("""
                SELECT ec.contract_id, ec.salary_definition_id, ec.start_date
                FROM employee_contract ec
                WHERE ec.employee_id = :eid
            """),
            {"eid": employee_id},
        ).fetchone()

        assert contract_row is not None, "employee_contract row missing"
        assert contract_row[1] == sal_def_row[0], (
            "Contract does not reference the correct salary_definition"
        )

        # -------------------------------------------------------------------
        # STEP 5 — Activate workspace
        #
        # DB trigger trg_enforce_workspace_live (migration 0daab4ac893b) blocks
        # any INSERT on payroll_run unless workspace.status = 'LIVE'.
        # -------------------------------------------------------------------
        db.execute(
            text("UPDATE workspace SET status = 'LIVE' WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )
        db.commit()

        # Confirm the update landed
        ws_status = db.execute(
            text("SELECT status FROM workspace WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).scalar()
        assert ws_status == "LIVE", f"Workspace status not LIVE: {ws_status}"

        # -------------------------------------------------------------------
        # STEP 6 — Run payroll
        #
        # POST /api/v1/payroll/run
        # Route:
        #   1. Loads employees via employee ⟶ employee_contract ⟶ salary_definition JOIN
        #   2. Loads tax_band rows WHERE statutory_rule_id = (highest version rule)
        #   3. Loads statutory_rule ORDER BY version DESC LIMIT 1
        #   4. Loads active payroll_rules WHERE workspace_id = :wid
        #   5. Delegates to execute_and_persist() → pure calc → DB persist
        # DB trigger: trg_enforce_workspace_live fires on INSERT payroll_run
        # DB trigger: trg_enforce_payroll_readiness fires on INSERT payroll_run
        # -------------------------------------------------------------------
        payroll_resp = client.post(
            "/api/v1/payroll/run",
            json={"workspace_id": str(workspace_id)},
        )

        assert payroll_resp.status_code == 200, (
            f"Payroll run HTTP status: {payroll_resp.status_code}\n{payroll_resp.text}"
        )
        payroll_body = payroll_resp.json()
        assert payroll_body["status"] == "success", (
            f"Payroll run failed: {payroll_body}"
        )

        payroll_run_id = payroll_body["payroll_run_id"]
        assert payroll_run_id is not None

        summary = payroll_body["summary"]
        assert summary["success_count"] == 1, (
            f"Expected 1 success, got: {summary}"
        )
        assert summary["failure_count"] == 0, (
            f"Expected 0 failures, got: {summary}"
        )

        # Summary totals are Decimal serialised to float by FastAPI
        assert float(summary["total_gross_pay"]) == float(GROSS)
        assert float(summary["total_net_pay"])   == float(EXPECTED_NET)

        # -------------------------------------------------------------------
        # STEP 7 — Verify payroll_run persisted (status + rules_context_snapshot)
        # -------------------------------------------------------------------
        run_row = db.execute(
            text("""
                SELECT status, rules_context_snapshot
                FROM payroll_run
                WHERE payroll_run_id = :run_id
            """),
            {"run_id": payroll_run_id},
        ).fetchone()

        assert run_row is not None, "payroll_run row not found in DB"
        # run_executor.py: failure_count == 0 → CALCULATING → CALCULATED
        assert run_row[0] == "CALCULATED", (
            f"Expected CALCULATED, got {run_row[0]}"
        )

        run_snapshot = run_row[1]
        assert run_snapshot is not None, "rules_context_snapshot must not be NULL"
        assert run_snapshot["statutory_rule"]["id"] == str(statutory_rule_id), (
            f"snapshot statutory_rule.id mismatch: {run_snapshot['statutory_rule']['id']}"
        )
        assert run_snapshot["statutory_rule"]["version"] == 9999, (
            f"snapshot statutory_rule.version mismatch: {run_snapshot['statutory_rule']['version']}"
        )
        assert isinstance(run_snapshot["payroll_rules"], list), (
            "snapshot payroll_rules must be a list"
        )

        # -------------------------------------------------------------------
        # STEP 8 — Verify payroll_result persisted + validate exact calculation
        #
        # calculations_snapshot_json stores Decimal values as strings via
        # _sanitize_json (json.dumps default=str). Float conversion handles this.
        #
        # Expected values — see EXPECTED_PAYE / EXPECTED_NET constants above.
        # Values are derived from 5-band PAYE + 9% statutory pension + 2.5% NHF.
        # -------------------------------------------------------------------
        result_row = db.execute(
            text("""
                SELECT
                    net_pay,
                    calculations_snapshot_json,
                    gross_components_jsonb,
                    status
                FROM payroll_result
                WHERE payroll_run_id = :run_id
            """),
            {"run_id": payroll_run_id},
        ).fetchone()

        assert result_row is not None, "payroll_result row not found in DB"

        net_pay   = float(result_row[0])
        snapshot  = result_row[1]   # JSONB → dict; Decimal values stored as strings
        gross_comp = result_row[2]  # JSONB → dict
        result_status = result_row[3]

        assert result_status == "SUCCESS"

        # net_pay column (Numeric) — direct assertion
        assert net_pay == float(EXPECTED_NET), (
            f"net_pay mismatch: expected {EXPECTED_NET}, got {net_pay}"
        )

        # calculations_snapshot_json — values stored as strings by _sanitize_json
        assert float(snapshot["gross"]) == float(GROSS), (
            f"snapshot.gross mismatch: expected {GROSS}, got {snapshot['gross']}"
        )
        assert float(snapshot["paye"]) == float(EXPECTED_PAYE), (
            f"snapshot.paye mismatch: expected {EXPECTED_PAYE}, got {snapshot['paye']}"
        )
        assert float(snapshot["net"]) == float(EXPECTED_NET), (
            f"snapshot.net mismatch: expected {EXPECTED_NET}, got {snapshot['net']}"
        )

        # gross_components_jsonb — component amounts stored as int/float (not Decimal)
        assert float(gross_comp["BASIC"]["amount"])     == float(BASIC)
        assert float(gross_comp["HOUSING"]["amount"])   == float(HOUSING)
        assert float(gross_comp["TRANSPORT"]["amount"]) == float(TRANSPORT)

    finally:
        # -------------------------------------------------------------------
        # Cleanup — delete in reverse FK dependency order.
        # Each statement scoped to the workspace or IDs created above so that
        # pre-existing data in other workspaces is not affected.
        # -------------------------------------------------------------------

        # Roll back any aborted transaction before starting cleanup
        db.rollback()

        # Bypass immutability triggers so cleanup succeeds at any lifecycle state
        db.execute(text("SET LOCAL session_replication_role = replica"))

        # payroll_result → FK to payroll_run and employee
        db.execute(
            text("""
                DELETE FROM payroll_result
                WHERE payroll_run_id IN (
                    SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid
                )
            """),
            {"wid": workspace_id},
        )

        # event_store — aggregate_id is payroll_run_id (no FK, but scoped by type)
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

        # audit_log → FK to workspace
        db.execute(
            text("DELETE FROM audit_log WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )

        # payroll_run → FK to workspace
        db.execute(
            text("DELETE FROM payroll_run WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )

        # employee_contract → FK to employee and salary_definition
        db.execute(
            text("""
                DELETE FROM employee_contract
                WHERE employee_id IN (
                    SELECT employee_id FROM employee WHERE workspace_id = :wid
                )
            """),
            {"wid": workspace_id},
        )

        # employee → FK to workspace
        db.execute(
            text("DELETE FROM employee WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )

        # payroll_rule → FK to workspace
        db.execute(
            text("DELETE FROM payroll_rule WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )

        # salary_definition → FK to workspace
        db.execute(
            text("DELETE FROM salary_definition WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )

        # tax_band → FK to statutory_rule (only the bands we inserted)
        db.execute(
            text("DELETE FROM tax_band WHERE statutory_rule_id = :sr_id"),
            {"sr_id": statutory_rule_id},
        )

        # statutory_rule — no FK
        db.execute(
            text("DELETE FROM statutory_rule WHERE statutory_rule_id = :sr_id"),
            {"sr_id": statutory_rule_id},
        )

        # component_metadata — no FK to workspace (platform-level)
        db.execute(
            text("""
                DELETE FROM component_metadata
                WHERE component_metadata_id = :cm_id
            """),
            {"cm_id": component_metadata_id},
        )

        # workspace → FK to account
        db.execute(
            text("DELETE FROM workspace WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )

        # account — no FK
        db.execute(
            text("DELETE FROM account WHERE account_id = :aid"),
            {"aid": account_id},
        )

        db.commit()
        db.close()
