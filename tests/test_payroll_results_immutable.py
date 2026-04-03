"""
Integration tests: payroll_result immutability after calculation.

Verifies that the trg_prevent_calculated_result_update /
trg_prevent_calculated_result_delete triggers block mutations once the
parent payroll_run has reached CALCULATED or any later status.

Tests
-----
1. test_update_blocked_after_calculation
   UPDATE on payroll_result raises InternalError when run is CALCULATED.

2. test_delete_blocked_after_calculation
   DELETE on payroll_result raises InternalError when run is CALCULATED.

3. test_update_blocked_after_approval
   UPDATE is still blocked after the run transitions to APPROVED.

4. test_update_blocked_after_lock
   UPDATE is still blocked after the run transitions to LOCKED.

5. test_update_allowed_before_calculation
   A direct UPDATE is permitted while the run is in PARTIAL status
   (retry in progress), confirming the trigger does not block the
   retry path.

Run:
    pytest tests/test_payroll_results_immutable.py -v
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import InternalError

from backend.api.main import app
from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal

client = TestClient(app)

BASIC     = 500_000
HOUSING   = 150_000
TRANSPORT =  75_000


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _create_prerequisites(db, account_id, workspace_id,
                           statutory_rule_id, component_metadata_id, stat_version):
    db.add(Account(account_id=account_id, name=f"Immutable Test Corp {stat_version}"))
    db.add(Workspace(
        workspace_id=workspace_id,
        account_id=account_id,
        name=f"Immutable Test Workspace {stat_version}",
        country_code="NG",
        base_currency="NGN",
        status="DRAFT",
    ))
    db.execute(
        text("""
            INSERT INTO statutory_rule (statutory_rule_id, state, version, rules_jsonb)
            VALUES (:id, 'NATIONAL', :ver, '{}')
        """),
        {"id": statutory_rule_id, "ver": stat_version},
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
            VALUES (:cm_id, 'TEST_SEED', 'NG', :ver, '{}', CURRENT_DATE, true)
        """),
        {"cm_id": component_metadata_id, "ver": stat_version},
    )
    db.commit()


def _onboard_and_run(workspace_id):
    payload = {
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
                "employee_number":        "EMP-IMM-001",
                "full_name":              "Immutable Test Employee",
                "salary_definition_name": "STANDARD",
                "biodata": {
                    "TIN":            "1231231230",
                    "BANK":           "First Bank",
                    "ACCOUNT_NUMBER": "1234567890",
                    "RSA":            "PEN600000001",
                    "FULL_NAME":      "Immutable Test Employee",
                },
            }
        ],
    }
    resp = client.post("/api/v1/onboarding/commit", json=payload)
    assert resp.status_code == 200, resp.text

    db = SessionLocal()
    db.execute(
        text("UPDATE workspace SET status = 'LIVE' WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    )
    db.commit()
    db.close()

    run_resp = client.post("/api/v1/payroll/run",
                           json={"workspace_id": str(workspace_id)})
    assert run_resp.status_code == 200, run_resp.text
    return run_resp.json()["payroll_run_id"]


def _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id):
    db.rollback()
    db.execute(text("SET LOCAL session_replication_role = replica"))

    db.execute(text("""
        DELETE FROM payroll_reconciliation
        WHERE payroll_run_id IN (
            SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid
        )
    """), {"wid": workspace_id})
    db.execute(text("""
        DELETE FROM payroll_result
        WHERE payroll_run_id IN (
            SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid
        )
    """), {"wid": workspace_id})
    db.execute(text("""
        DELETE FROM event_store
        WHERE aggregate_type = 'PAYROLL_RUN'
          AND aggregate_id IN (
            SELECT payroll_run_id FROM payroll_run WHERE workspace_id = :wid
          )
    """), {"wid": workspace_id})
    db.execute(text("DELETE FROM audit_log WHERE workspace_id = :wid"),
               {"wid": workspace_id})
    db.execute(text("DELETE FROM payroll_run WHERE workspace_id = :wid"),
               {"wid": workspace_id})
    db.execute(text("""
        DELETE FROM employee_contract
        WHERE employee_id IN (
            SELECT employee_id FROM employee WHERE workspace_id = :wid
        )
    """), {"wid": workspace_id})
    db.execute(text("DELETE FROM employee WHERE workspace_id = :wid"),
               {"wid": workspace_id})
    db.execute(text("DELETE FROM payroll_rule WHERE workspace_id = :wid"),
               {"wid": workspace_id})
    db.execute(text("DELETE FROM salary_definition WHERE workspace_id = :wid"),
               {"wid": workspace_id})
    db.execute(text("DELETE FROM tax_band WHERE statutory_rule_id = :sr_id"),
               {"sr_id": statutory_rule_id})
    db.execute(text("DELETE FROM statutory_rule WHERE statutory_rule_id = :sr_id"),
               {"sr_id": statutory_rule_id})
    db.execute(text("DELETE FROM component_metadata WHERE component_metadata_id = :cm_id"),
               {"cm_id": component_metadata_id})
    db.execute(text("DELETE FROM workspace WHERE workspace_id = :wid"),
               {"wid": workspace_id})
    db.execute(text("DELETE FROM account WHERE account_id = :aid"),
               {"aid": account_id})
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# Test 1: UPDATE blocked when run is CALCULATED
# ---------------------------------------------------------------------------

def test_update_blocked_after_calculation():
    """trg_prevent_calculated_result_update must block UPDATE on CALCULATED run."""
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()
    try:
        _create_prerequisites(db, account_id, workspace_id,
                               statutory_rule_id, component_metadata_id, 9045)
        run_id = _onboard_and_run(workspace_id)

        # Confirm run is CALCULATED
        status = db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).scalar()
        assert status == "CALCULATED", f"Precondition: expected CALCULATED, got {status}"

        # Attempt UPDATE — must be blocked
        with pytest.raises(InternalError, match="immutable after calculation"):
            db.execute(
                text("""
                    UPDATE payroll_result
                    SET    net_pay = 0
                    WHERE  payroll_run_id = :rid
                """),
                {"rid": run_id},
            )
            db.commit()

        db.rollback()

        # net_pay must be unchanged
        original_net = db.execute(
            text("SELECT net_pay FROM payroll_result WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).scalar()
        assert original_net != 0, "net_pay must not have been altered"

    finally:
        _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id)


# ---------------------------------------------------------------------------
# Test 2: DELETE blocked when run is CALCULATED
# ---------------------------------------------------------------------------

def test_delete_blocked_after_calculation():
    """trg_prevent_calculated_result_delete must block DELETE on CALCULATED run."""
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()
    try:
        _create_prerequisites(db, account_id, workspace_id,
                               statutory_rule_id, component_metadata_id, 9044)
        run_id = _onboard_and_run(workspace_id)

        count_before = db.execute(
            text("SELECT COUNT(*) FROM payroll_result WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).scalar()
        assert count_before > 0, "Precondition: results must exist"

        with pytest.raises(InternalError, match="immutable after calculation"):
            db.execute(
                text("DELETE FROM payroll_result WHERE payroll_run_id = :rid"),
                {"rid": run_id},
            )
            db.commit()

        db.rollback()

        count_after = db.execute(
            text("SELECT COUNT(*) FROM payroll_result WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).scalar()
        assert count_after == count_before, "Row count must be unchanged after blocked DELETE"

    finally:
        _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id)


# ---------------------------------------------------------------------------
# Test 3: UPDATE still blocked after APPROVED
# ---------------------------------------------------------------------------

def test_update_blocked_after_approval():
    """Immutability persists after CALCULATED → APPROVED transition."""
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()
    try:
        _create_prerequisites(db, account_id, workspace_id,
                               statutory_rule_id, component_metadata_id, 9043)
        run_id = _onboard_and_run(workspace_id)

        approve_resp = client.post(f"/api/v1/payroll/run/{run_id}/approve")
        assert approve_resp.status_code == 200, approve_resp.text
        assert approve_resp.json()["run_status"] == "APPROVED"

        with pytest.raises(InternalError, match="immutable after calculation"):
            db.execute(
                text("""
                    UPDATE payroll_result
                    SET    net_pay = 0
                    WHERE  payroll_run_id = :rid
                """),
                {"rid": run_id},
            )
            db.commit()

        db.rollback()

    finally:
        _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id)


# ---------------------------------------------------------------------------
# Test 4: UPDATE still blocked after LOCKED
# ---------------------------------------------------------------------------

def test_update_blocked_after_lock():
    """Immutability persists after CALCULATED → APPROVED → LOCKED transition."""
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()
    try:
        _create_prerequisites(db, account_id, workspace_id,
                               statutory_rule_id, component_metadata_id, 9042)
        run_id = _onboard_and_run(workspace_id)

        client.post(f"/api/v1/payroll/run/{run_id}/approve")
        lock_resp = client.post(f"/api/v1/payroll/run/{run_id}/lock")
        assert lock_resp.status_code == 200, lock_resp.text
        assert lock_resp.json()["run_status"] == "LOCKED"

        with pytest.raises(InternalError, match="immutable after calculation"):
            db.execute(
                text("""
                    UPDATE payroll_result
                    SET    net_pay = 0
                    WHERE  payroll_run_id = :rid
                """),
                {"rid": run_id},
            )
            db.commit()

        db.rollback()

    finally:
        _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id)


# ---------------------------------------------------------------------------
# Test 5: Mutations allowed during PARTIAL (retry path is not blocked)
# ---------------------------------------------------------------------------

def test_update_allowed_during_partial():
    """The trigger must NOT block updates when run status is PARTIAL.

    The retry service updates FAILED payroll_result rows to SUCCESS.
    Blocking PARTIAL would break the retry flow.

    This test forces the run into PARTIAL via a direct status update
    (bypassing the engine) and verifies that payroll_result can still
    be modified.
    """
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()
    try:
        _create_prerequisites(db, account_id, workspace_id,
                               statutory_rule_id, component_metadata_id, 9041)
        run_id = _onboard_and_run(workspace_id)

        # Force run back to PARTIAL to simulate the retry scenario.
        # Use session_replication_role to bypass the state-machine trigger
        # (which would otherwise reject CALCULATED → PARTIAL reversal).
        db.execute(text("SET LOCAL session_replication_role = replica"))
        db.execute(
            text("UPDATE payroll_run SET status = 'PARTIAL' WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        )
        db.commit()

        # UPDATE on payroll_result must now succeed (no exception raised)
        original_net = db.execute(
            text("SELECT net_pay FROM payroll_result WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).scalar()

        db.execute(
            text("""
                UPDATE payroll_result
                SET    net_pay = net_pay + 0
                WHERE  payroll_run_id = :rid
            """),
            {"rid": run_id},
        )
        db.commit()

        # Restore to CALCULATED for clean teardown
        db.execute(text("SET LOCAL session_replication_role = replica"))
        db.execute(
            text("UPDATE payroll_run SET status = 'CALCULATED' WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        )
        db.commit()

    finally:
        _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id)
