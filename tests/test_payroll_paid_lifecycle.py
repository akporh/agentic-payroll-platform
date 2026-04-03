"""
Integration tests: Payroll PAID lifecycle.

Validates the LOCKED → PAID transition and its immutability guarantee.

Tests
-----
1. test_locked_to_paid_transition
   Full happy-path: run payroll → approve → lock → pay.
   Asserts the API returns PAID and the DB row reflects PAID.

2. test_paid_transition_requires_locked_state
   Attempting LOCKED → PAID on a run that is only CALCULATED (not yet
   approved or locked) must be rejected with 400.

3. test_paid_run_is_immutable
   After PAID the DB trigger trg_prevent_paid_run_update must block any
   UPDATE attempt, raising an InternalError.

4. test_paid_transition_writes_audit_entry
   mark_payroll_run_paid must write one audit_log row with
   action='STATUS_TRANSITION' and new_value_jsonb.status='PAID'.

5. test_paid_state_machine_unit
   Pure unit test — verifies the Python state machine allows LOCKED → PAID
   and rejects any other transition from PAID.

Prerequisites
-------------
- PostgreSQL at DATABASE_URL.
- All Alembic migrations applied.

Run:
    pytest tests/test_payroll_paid_lifecycle.py -v
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import InternalError

from backend.api.main import app
from backend.domain.payroll.state_machine import ALLOWED_TRANSITIONS, transition
from backend.domain.payroll.status import PayrollRunStatus
from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal

client = TestClient(app)

BASIC     = 500_000
HOUSING   = 150_000
TRANSPORT =  75_000


# ---------------------------------------------------------------------------
# Shared fixture helpers
# ---------------------------------------------------------------------------

def _create_prerequisites(db, account_id, workspace_id, statutory_rule_id,
                           component_metadata_id, stat_version):
    db.add(Account(account_id=account_id, name=f"PAID Test Corp {stat_version}"))
    db.add(Workspace(
        workspace_id=workspace_id,
        account_id=account_id,
        name=f"PAID Test Workspace {stat_version}",
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
    """Onboard one employee and execute a payroll run. Returns payroll_run_id."""
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
                "employee_number":        "EMP-PAID-001",
                "full_name":              "PAID Test Employee",
                "salary_definition_name": "STANDARD",
                "biodata": {
                    "TIN":            "1122334455",
                    "BANK":           "GTBank",
                    "ACCOUNT_NUMBER": "0123456789",
                    "RSA":            "PEN300000001",
                    "FULL_NAME":      "PAID Test Employee",
                },
            }
        ],
    }
    commit_resp = client.post("/api/v1/onboarding/commit", json=payload)
    assert commit_resp.status_code == 200, commit_resp.text

    db = SessionLocal()
    db.execute(
        text("UPDATE workspace SET status = 'LIVE' WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    )
    db.commit()
    db.close()

    run_resp = client.post("/api/v1/payroll/run", json={"workspace_id": str(workspace_id)})
    assert run_resp.status_code == 200, run_resp.text
    return run_resp.json()["payroll_run_id"]


def _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id):
    db.rollback()
    # Bypass immutability triggers (trg_prevent_paid_result_delete,
    # trg_prevent_paid_run_delete) so teardown always succeeds regardless of
    # the lifecycle state the run was left in.
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


# ---------------------------------------------------------------------------
# Test 1: Full LOCKED → PAID happy path via API
# ---------------------------------------------------------------------------

def test_locked_to_paid_transition():
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()
    try:
        _create_prerequisites(db, account_id, workspace_id,
                               statutory_rule_id, component_metadata_id, 9076)

        run_id = _onboard_and_run(workspace_id)

        # Approve
        approve_resp = client.post(f"/api/v1/payroll/run/{run_id}/approve")
        assert approve_resp.status_code == 200, approve_resp.text
        assert approve_resp.json()["run_status"] == "APPROVED"

        # Lock
        lock_resp = client.post(f"/api/v1/payroll/run/{run_id}/lock")
        assert lock_resp.status_code == 200, lock_resp.text
        assert lock_resp.json()["run_status"] == "LOCKED"

        # Pay
        pay_resp = client.post(
            f"/api/v1/payroll/run/{run_id}/pay",
            json={"actor_id": "finance@company.com"},
        )
        assert pay_resp.status_code == 200, pay_resp.text
        body = pay_resp.json()
        assert body["run_status"] == "PAID"
        assert body["run_id"] == run_id

        # Confirm DB row
        db_status = db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).scalar()
        assert db_status == "PAID"

    finally:
        _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id)


# ---------------------------------------------------------------------------
# Test 2: Attempt PAID on a non-LOCKED run is rejected
# ---------------------------------------------------------------------------

def test_paid_transition_requires_locked_state():
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()
    try:
        _create_prerequisites(db, account_id, workspace_id,
                               statutory_rule_id, component_metadata_id, 9075)

        run_id = _onboard_and_run(workspace_id)

        # Run is CALCULATED at this point — attempt /pay directly (skip approve+lock)
        pay_resp = client.post(
            f"/api/v1/payroll/run/{run_id}/pay",
            json={"actor_id": "finance@company.com"},
        )
        assert pay_resp.status_code == 400
        assert "Invalid transition" in pay_resp.json()["detail"]

        # Status must remain CALCULATED
        db_status = db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).scalar()
        assert db_status == "CALCULATED"

    finally:
        _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id)


# ---------------------------------------------------------------------------
# Test 3: PAID run is immutable at the DB level
# ---------------------------------------------------------------------------

def test_paid_run_is_immutable():
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()
    try:
        _create_prerequisites(db, account_id, workspace_id,
                               statutory_rule_id, component_metadata_id, 9074)

        run_id = _onboard_and_run(workspace_id)

        client.post(f"/api/v1/payroll/run/{run_id}/approve")
        client.post(f"/api/v1/payroll/run/{run_id}/lock")
        client.post(f"/api/v1/payroll/run/{run_id}/pay",
                    json={"actor_id": "finance@company.com"})

        # DB trigger trg_prevent_paid_run_update must block any UPDATE
        with pytest.raises(InternalError):
            db.execute(
                text("""
                    UPDATE payroll_run
                    SET    status = 'LOCKED'
                    WHERE  payroll_run_id = :rid
                """),
                {"rid": run_id},
            )
            db.commit()

        db.rollback()

        # Status still PAID after the rejected update
        db_status = db.execute(
            text("SELECT status FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).scalar()
        assert db_status == "PAID"

    finally:
        _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id)


# ---------------------------------------------------------------------------
# Test 4: PAID transition writes an audit_log entry
# ---------------------------------------------------------------------------

def test_paid_transition_writes_audit_entry():
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()
    try:
        _create_prerequisites(db, account_id, workspace_id,
                               statutory_rule_id, component_metadata_id, 9073)

        run_id = _onboard_and_run(workspace_id)

        client.post(f"/api/v1/payroll/run/{run_id}/approve")
        client.post(f"/api/v1/payroll/run/{run_id}/lock")
        client.post(
            f"/api/v1/payroll/run/{run_id}/pay",
            json={"actor_id": "finance@company.com"},
        )

        audit_rows = db.execute(
            text("""
                SELECT action, old_value_jsonb, new_value_jsonb, performed_by
                FROM   audit_log
                WHERE  workspace_id = :wid
                  AND  entity_id    = :rid
                  AND  action       = 'STATUS_TRANSITION'
                ORDER  BY performed_at ASC
            """),
            {"wid": workspace_id, "rid": run_id},
        ).fetchall()

        # A complete run produces 5 audit records:
        # CALCULATING, CALCULATED, APPROVED, LOCKED, PAID
        assert len(audit_rows) == 5, (
            f"Expected 5 audit rows, got {len(audit_rows)}: {audit_rows}"
        )

        paid_row = audit_rows[4]
        assert paid_row[0] == "STATUS_TRANSITION"
        assert paid_row[1]["status"] == "LOCKED"   # old_value_jsonb
        assert paid_row[2]["status"] == "PAID"     # new_value_jsonb
        assert paid_row[3] == "finance@company.com"  # performed_by (actor_id passed in)

    finally:
        _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id)


# ---------------------------------------------------------------------------
# Test 5: State machine unit test — no DB required
# ---------------------------------------------------------------------------

def test_paid_state_machine_unit():
    # LOCKED → PAID must be allowed
    assert PayrollRunStatus.PAID in ALLOWED_TRANSITIONS[PayrollRunStatus.LOCKED]

    result = transition(PayrollRunStatus.LOCKED, PayrollRunStatus.PAID)
    assert result == PayrollRunStatus.PAID

    # PAID is terminal — no outgoing transitions
    assert ALLOWED_TRANSITIONS[PayrollRunStatus.PAID] == []

    # PAID → anything must raise
    for target in PayrollRunStatus:
        if target == PayrollRunStatus.PAID:
            continue
        with pytest.raises(ValueError, match="Invalid transition"):
            transition(PayrollRunStatus.PAID, target)

    # Transitions that skip PAID (e.g. CALCULATED → PAID) must also raise
    with pytest.raises(ValueError, match="Invalid transition"):
        transition(PayrollRunStatus.CALCULATED, PayrollRunStatus.PAID)

    with pytest.raises(ValueError, match="Invalid transition"):
        transition(PayrollRunStatus.APPROVED, PayrollRunStatus.PAID)
