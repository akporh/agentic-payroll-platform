"""
End-to-end integration test: payroll lock and approval.

Validates that once a payroll run is APPROVED or LOCKED, all mutation
attempts are rejected and no data changes occur.

Status lifecycle tested
-----------------------
  CALCULATED  →  APPROVED  →  LOCKED

  At each locked state, the following mutation is attempted:
    POST /payroll/run/{run_id}/retry

  All attempts must:
  - Return HTTP 400
  - Leave payroll_run.status unchanged
  - Leave payroll_result row count unchanged
  - Leave per-employee net_pay unchanged

Additional state machine assertions
------------------------------------
  - Approving a non-CALCULATED run returns 400.
  - Locking a non-APPROVED run returns 400.
  - Approving an already-APPROVED run returns 400 (state machine rejects
    APPROVED → APPROVED as an invalid transition).

Where locking is enforced
--------------------------
Python layer (payroll_retry_service.py):
  Explicit guard: current_status in ("APPROVED", "LOCKED") → ValueError.
  This is caught by the route and returned as HTTP 400.

DB layer:
  The DB trigger trg_payroll_run_state_machine (migration 9901bc4ed0c5)
  only enforces the legacy DRAFT/PROCESSING/COMPLETED/PAID states.
  APPROVED and LOCKED fall through the trigger to RETURN NEW and are
  therefore permissible at the DB level — protection is Python-only for
  these two states.

Requirements
------------
- PostgreSQL running at DATABASE_URL env var.
- All Alembic migrations applied.
- This test uses statutory_rule version=9996 so it wins ORDER BY version
  DESC when the three earlier tests (9999, 9998, 9997) are absent.

Run:
    pytest tests/test_payroll_lock_and_approval.py -v
"""

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.api.main import app
from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal

client = TestClient(app)

# ---------------------------------------------------------------------------
# Salary for the single test employee
# ---------------------------------------------------------------------------
BASIC     = 500_000
HOUSING   = 200_000
TRANSPORT = 100_000
GROSS     = BASIC + HOUSING + TRANSPORT          # 800_000
# 5-band PAYE + 8% explicit pension (rules_jsonb pension.employee_rate=0.08).
# No NHF workspace rule is configured so NHF is not deducted.
#   Pension = GROSS × 8% = 64 000
#   Annual taxable = (800k - 64k) × 12 = 8 832 000 → Monthly PAYE = 145 226.67
#   NET = 800 000 - 64 000 - 145 226.67 = 590 773.33
EXPECTED_PAYE = 145_226.67
EXPECTED_NET  = 590_773.33


def test_payroll_approval_and_lock_e2e():
    """
    Full approval + lock lifecycle.

    Phase 1  — Run payroll successfully → CALCULATED
    Phase 2  — Approve → APPROVED
               Assert retry is rejected (400)
               Assert result rows and values unchanged
    Phase 3  — Lock → LOCKED
               Assert retry is rejected (400)
               Assert result rows and values unchanged
    Phase 4  — State machine boundary checks
               Assert approving an APPROVED run is rejected (400)
               Assert locking a CALCULATED run (not yet APPROVED) is rejected
    """

    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()

    try:
        # -------------------------------------------------------------------
        # STEP 1 — Prerequisites
        # -------------------------------------------------------------------

        db.add(Account(
            account_id=account_id,
            name="Lock Approval Test Corp",
        ))

        db.add(Workspace(
            workspace_id=workspace_id,
            account_id=account_id,
            name="Lock Approval Test Workspace",
            country_code="NG",
            base_currency="NGN",
            status="DRAFT",
        ))

        # version=9996 wins when pipeline (9999), partial (9998), retry (9997)
        # tests are not running concurrently
        db.execute(
            text("""
                INSERT INTO statutory_rule
                    (statutory_rule_id, state, version, rules_jsonb, country_code, effective_from)
                VALUES (:id, 'NATIONAL', 9996, '{"pension": {"employee_rate": 0.08, "employer_rate": 0.10}}', 'NG', '2026-04-01')
            """),
            {"id": statutory_rule_id},
        )

        for lower, upper, rate in [
            (0,         300_000,   0.07),
            (300_000,   600_000,   0.11),
            (600_000,   1_100_000, 0.15),
            (1_100_000, 1_600_000, 0.19),
            (1_600_000, None,      0.21),
        ]:
            db.execute(
                text("""
                    INSERT INTO tax_band
                        (tax_band_id, statutory_rule_id, lower_limit, upper_limit, rate)
                    VALUES (gen_random_uuid(), :sr_id, :lower, :upper, :rate)
                """),
                {"sr_id": statutory_rule_id, "lower": lower, "upper": upper, "rate": rate},
            )

        db.execute(
            text("""
                INSERT INTO component_metadata
                    (component_metadata_id, component_code, country_code, version,
                     metadata_json, effective_from, is_active)
                VALUES (:cm_id, 'TEST_SEED', 'NG', 9996, '{}', CURRENT_DATE, true)
            """),
            {"cm_id": component_metadata_id},
        )

        db.commit()

        # -------------------------------------------------------------------
        # STEP 2 — Onboard one employee via commit endpoint
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
        assert commit_resp.status_code == 200, commit_resp.text
        assert commit_resp.json()["status"] == "success"

        # -------------------------------------------------------------------
        # STEP 3 — Activate workspace, run payroll → CALCULATED
        # -------------------------------------------------------------------
        db.execute(
            text("UPDATE workspace SET status = 'LIVE' WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        )
        db.commit()

        payroll_resp = client.post(
            "/api/v1/payroll/run",
            json={"workspace_id": str(workspace_id)},
        )
        assert payroll_resp.status_code == 200, payroll_resp.text
        body = payroll_resp.json()
        assert body["status"] == "success"

        payroll_run_id = body["payroll_run_id"]

        # Confirm CALCULATED status and single SUCCESS result
        run_status = db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": payroll_run_id},
        ).scalar()
        assert run_status == "CALCULATED", f"Expected CALCULATED, got {run_status}"

        def fetch_result_rows():
            return db.execute(
                text("""
                    SELECT employee_id, status, net_pay
                    FROM payroll_result
                    WHERE payroll_run_id = :rid
                """),
                {"rid": payroll_run_id},
            ).fetchall()

        rows_before = fetch_result_rows()
        assert len(rows_before) == 1
        assert rows_before[0][1] == "SUCCESS"
        assert float(rows_before[0][2]) == float(EXPECTED_NET)

        # -------------------------------------------------------------------
        # STEP 4 — State machine boundary: lock before approve must fail
        #
        # CALCULATED → LOCKED is not an allowed transition (must go via
        # APPROVED). This verifies the Python state machine is enforced.
        # -------------------------------------------------------------------
        premature_lock = client.post(f"/api/v1/payroll/run/{payroll_run_id}/lock")
        assert premature_lock.status_code == 400, (
            f"Expected 400 for locking a CALCULATED run, got {premature_lock.status_code}: "
            f"{premature_lock.text}"
        )

        # Run status must be unchanged
        assert db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": payroll_run_id},
        ).scalar() == "CALCULATED"

        # -------------------------------------------------------------------
        # PHASE 2 — Approve the run (CALCULATED → APPROVED)
        # -------------------------------------------------------------------

        # STEP 5 — Approve
        approve_resp = client.post(f"/api/v1/payroll/run/{payroll_run_id}/approve")
        assert approve_resp.status_code == 200, (
            f"Approve HTTP {approve_resp.status_code}: {approve_resp.text}"
        )
        approve_body = approve_resp.json()
        assert approve_body["status"]     == "success"
        assert approve_body["run_status"] == "APPROVED"
        assert db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": payroll_run_id},
        ).scalar() == "APPROVED"

        # STEP 6 — Retry an APPROVED run must be rejected
        retry_on_approved = client.post(f"/api/v1/payroll/run/{payroll_run_id}/retry")
        assert retry_on_approved.status_code == 400, (
            f"Expected 400 for retry on APPROVED run, got {retry_on_approved.status_code}: "
            f"{retry_on_approved.text}"
        )
        assert "APPROVED" in retry_on_approved.json()["detail"], (
            f"Error message should mention APPROVED: {retry_on_approved.json()}"
        )

        # STEP 7 — Assert run status unchanged after rejected retry
        assert db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": payroll_run_id},
        ).scalar() == "APPROVED", "Status must remain APPROVED after rejected retry"

        # STEP 8 — Assert no new result rows were created
        rows_after_approved_retry = fetch_result_rows()
        assert len(rows_after_approved_retry) == len(rows_before), (
            f"Result row count must not change: before={len(rows_before)}, "
            f"after={len(rows_after_approved_retry)}"
        )
        assert float(rows_after_approved_retry[0][2]) == float(EXPECTED_NET), (
            "net_pay must be unchanged after rejected retry"
        )

        # STEP 9 — Approving an already-APPROVED run must fail
        #          (APPROVED → APPROVED is not in the state machine)
        double_approve = client.post(f"/api/v1/payroll/run/{payroll_run_id}/approve")
        assert double_approve.status_code == 400, (
            f"Expected 400 for double-approve, got {double_approve.status_code}"
        )

        # -------------------------------------------------------------------
        # PHASE 3 — Lock the run (APPROVED → LOCKED)
        # -------------------------------------------------------------------

        # STEP 10 — Lock
        lock_resp = client.post(f"/api/v1/payroll/run/{payroll_run_id}/lock")
        assert lock_resp.status_code == 200, (
            f"Lock HTTP {lock_resp.status_code}: {lock_resp.text}"
        )
        assert db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": payroll_run_id},
        ).scalar() == "LOCKED"

        # STEP 11 — Retry a LOCKED run must be rejected
        retry_on_locked = client.post(f"/api/v1/payroll/run/{payroll_run_id}/retry")
        assert retry_on_locked.status_code == 400, (
            f"Expected 400 for retry on LOCKED run, got {retry_on_locked.status_code}: "
            f"{retry_on_locked.text}"
        )
        assert "LOCKED" in retry_on_locked.json()["detail"], (
            f"Error message should mention LOCKED: {retry_on_locked.json()}"
        )

        # STEP 12 — Assert run status still LOCKED
        assert db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": payroll_run_id},
        ).scalar() == "LOCKED", "Status must remain LOCKED after rejected retry"

        # STEP 13 — Assert no new result rows after locked retry rejection
        rows_after_locked_retry = fetch_result_rows()
        assert len(rows_after_locked_retry) == len(rows_before), (
            "Result row count must not change after rejected retry on LOCKED run"
        )
        assert float(rows_after_locked_retry[0][2]) == float(EXPECTED_NET), (
            "net_pay must be unchanged after rejected retry on LOCKED run"
        )

        # STEP 14 — Locking an already-LOCKED run must fail
        #           (LOCKED → LOCKED is not in the state machine)
        double_lock = client.post(f"/api/v1/payroll/run/{payroll_run_id}/lock")
        assert double_lock.status_code == 400, (
            f"Expected 400 for double-lock, got {double_lock.status_code}"
        )

    finally:
        # -------------------------------------------------------------------
        # Cleanup — reverse FK order, scoped to this test's IDs only.
        # payroll_run.status may be LOCKED; bypass immutability triggers
        # (trg_prevent_calculated_result_delete covers CALCULATED/APPROVED/
        # LOCKED/PAID) so teardown always succeeds.
        # -------------------------------------------------------------------
        db.rollback()
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
