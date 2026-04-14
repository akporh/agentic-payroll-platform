"""
Integration tests: payroll reconciliation.

Verifies the reconcile_payroll_run service and the POST/GET
/payroll/run/{run_id}/reconcile endpoints.

Tests
-----
1. test_reconcile_matched
   Run payroll, then POST reconcile with actual_total == engine total.
   Expects status=MATCHED, reconciled_at set, DB row correct.

2. test_reconcile_mismatch
   Run payroll, then POST reconcile with actual_total != engine total.
   Expects status=MISMATCH, DB row correct.

3. test_reconcile_duplicate_rejected
   Attempting to reconcile the same run twice returns HTTP 409.

4. test_reconcile_unknown_run
   Reconciling a non-existent run_id returns HTTP 404.

5. test_get_reconciliation
   After reconciling, GET /reconcile returns the record.

6. test_get_reconciliation_not_found
   GET /reconcile on an unreconciled run returns HTTP 404.

7. test_db_constraints_matched_requires_equal_totals
   DB CHECK constraint chk_matched_totals_equal rejects MATCHED with
   actual_total != expected_total.

8. test_db_constraints_mismatch_requires_unequal_totals
   DB CHECK constraint chk_mismatch_totals_differ rejects MISMATCH with
   actual_total == expected_total.

Run:
    pytest tests/test_payroll_reconciliation_e2e.py -v
"""

import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from backend.api.main import app
from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal

client = TestClient(app)

BASIC     = 500_000
HOUSING   = 150_000
TRANSPORT =  75_000
GROSS     = BASIC + HOUSING + TRANSPORT  # 725_000

# PAYE on 725_000 using bands seeded below:
#  0 – 300 000     @ 7%  = 21 000
#  300 000 – 600 000  @ 11% = 33 000
#  600 000 – 725 000  @ 15% = 18 750
EXPECTED_PAYE    = Decimal("72750")
EXPECTED_NET     = Decimal(GROSS) - EXPECTED_PAYE   # 652_250


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_prerequisites(db, account_id, workspace_id,
                           statutory_rule_id, component_metadata_id, stat_version):
    db.add(Account(account_id=account_id, name=f"Recon Test Corp {stat_version}"))
    db.add(Workspace(
        workspace_id=workspace_id,
        account_id=account_id,
        name=f"Recon Test Workspace {stat_version}",
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
                "employee_number":        "EMP-RECON-001",
                "full_name":              "Recon Test Employee",
                "salary_definition_name": "STANDARD",
                "biodata": {
                    "TIN":            "9988776655",
                    "BANK":           "Access Bank",
                    "ACCOUNT_NUMBER": "9876543210",
                    "RSA":            "PEN500000001",
                    "FULL_NAME":      "Recon Test Employee",
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
# Test 1: MATCHED reconciliation
# ---------------------------------------------------------------------------

def test_reconcile_matched():
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()
    try:
        _create_prerequisites(db, account_id, workspace_id,
                               statutory_rule_id, component_metadata_id, 9055)
        run_id = _onboard_and_run(workspace_id)
        client.post(f"/api/v1/payroll/run/{run_id}/approve")
        client.post(f"/api/v1/payroll/run/{run_id}/lock")

        # Fetch the engine total from the DB
        engine_net = db.execute(
            text("SELECT total_net_pay FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).scalar()
        assert engine_net is not None

        # Reconcile with exact match
        resp = client.post(
            f"/api/v1/payroll/run/{run_id}/reconcile",
            json={"actual_total": float(engine_net)},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        recon = body["reconciliation"]

        assert recon["status"] == "MATCHED"
        assert Decimal(str(recon["expected_total"])) == Decimal(str(engine_net))
        assert Decimal(str(recon["actual_total"]))   == Decimal(str(engine_net))
        assert recon["reconciled_at"] is not None
        assert recon["payroll_run_id"] == run_id

        # Confirm DB row
        db_row = db.execute(
            text("""
                SELECT status, expected_total, actual_total
                FROM   payroll_reconciliation
                WHERE  payroll_run_id = :rid
            """),
            {"rid": run_id},
        ).fetchone()
        assert db_row is not None
        assert db_row[0] == "MATCHED"
        assert db_row[1] == db_row[2]  # expected == actual

    finally:
        _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id)


# ---------------------------------------------------------------------------
# Test 2: MISMATCH reconciliation
# ---------------------------------------------------------------------------

def test_reconcile_mismatch():
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()
    try:
        _create_prerequisites(db, account_id, workspace_id,
                               statutory_rule_id, component_metadata_id, 9054)
        run_id = _onboard_and_run(workspace_id)
        client.post(f"/api/v1/payroll/run/{run_id}/approve")
        client.post(f"/api/v1/payroll/run/{run_id}/lock")

        engine_net = db.execute(
            text("SELECT total_net_pay FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).scalar()

        wrong_amount = float(engine_net) + 1000.00

        resp = client.post(
            f"/api/v1/payroll/run/{run_id}/reconcile",
            json={"actual_total": wrong_amount},
        )
        assert resp.status_code == 200, resp.text
        recon = resp.json()["reconciliation"]

        assert recon["status"] == "MISMATCH"
        assert Decimal(str(recon["expected_total"])) != Decimal(str(recon["actual_total"]))
        assert recon["reconciled_at"] is not None

    finally:
        _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id)


# ---------------------------------------------------------------------------
# Test 3: Duplicate reconciliation is rejected with 409
# ---------------------------------------------------------------------------

def test_reconcile_duplicate_rejected():
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()
    try:
        _create_prerequisites(db, account_id, workspace_id,
                               statutory_rule_id, component_metadata_id, 9053)
        run_id = _onboard_and_run(workspace_id)
        client.post(f"/api/v1/payroll/run/{run_id}/approve")
        client.post(f"/api/v1/payroll/run/{run_id}/lock")

        engine_net = db.execute(
            text("SELECT total_net_pay FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).scalar()

        # First reconciliation — must succeed
        resp1 = client.post(
            f"/api/v1/payroll/run/{run_id}/reconcile",
            json={"actual_total": float(engine_net)},
        )
        assert resp1.status_code == 200, resp1.text

        # Second reconciliation for same run — must be rejected
        resp2 = client.post(
            f"/api/v1/payroll/run/{run_id}/reconcile",
            json={"actual_total": float(engine_net)},
        )
        assert resp2.status_code == 409, (
            f"Expected 409 for duplicate reconciliation, got {resp2.status_code}: {resp2.text}"
        )
        assert "already exists" in resp2.json()["detail"].lower()

    finally:
        _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id)


# ---------------------------------------------------------------------------
# Test 4: Reconciling an unknown run returns 404
# ---------------------------------------------------------------------------

def test_reconcile_unknown_run():
    fake_id = str(uuid.uuid4())
    resp = client.post(
        f"/api/v1/payroll/run/{fake_id}/reconcile",
        json={"actual_total": 100000.00},
    )
    assert resp.status_code == 404, (
        f"Expected 404 for unknown run, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 5: GET returns the existing reconciliation record
# ---------------------------------------------------------------------------

def test_get_reconciliation():
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()
    try:
        _create_prerequisites(db, account_id, workspace_id,
                               statutory_rule_id, component_metadata_id, 9052)
        run_id = _onboard_and_run(workspace_id)
        client.post(f"/api/v1/payroll/run/{run_id}/approve")
        client.post(f"/api/v1/payroll/run/{run_id}/lock")

        engine_net = db.execute(
            text("SELECT total_net_pay FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": run_id},
        ).scalar()

        client.post(
            f"/api/v1/payroll/run/{run_id}/reconcile",
            json={"actual_total": float(engine_net)},
        )

        resp = client.get(f"/api/v1/payroll/run/{run_id}/reconcile")
        assert resp.status_code == 200, resp.text
        recon = resp.json()["reconciliation"]
        assert recon["payroll_run_id"] == run_id
        assert recon["status"] == "MATCHED"

    finally:
        _cleanup(db, workspace_id, statutory_rule_id, component_metadata_id, account_id)


# ---------------------------------------------------------------------------
# Test 6: GET returns 404 when no reconciliation exists
# ---------------------------------------------------------------------------

def test_get_reconciliation_not_found():
    fake_id = str(uuid.uuid4())
    resp = client.get(f"/api/v1/payroll/run/{fake_id}/reconcile")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Test 7: DB constraint rejects MATCHED with unequal totals
# ---------------------------------------------------------------------------

def test_db_constraints_matched_requires_equal_totals():
    db = SessionLocal()
    run_id = str(uuid.uuid4())
    try:
        with pytest.raises(IntegrityError):
            db.execute(
                text("""
                    INSERT INTO payroll_reconciliation
                        (payroll_run_id, expected_total, actual_total, status)
                    VALUES (:rid, 100000, 99000, 'MATCHED')
                """),
                {"rid": run_id},
            )
            db.commit()
    finally:
        db.rollback()
        db.close()


# ---------------------------------------------------------------------------
# Test 8: DB constraint rejects MISMATCH with equal totals
# ---------------------------------------------------------------------------

def test_db_constraints_mismatch_requires_unequal_totals():
    db = SessionLocal()
    run_id = str(uuid.uuid4())
    try:
        with pytest.raises(IntegrityError):
            db.execute(
                text("""
                    INSERT INTO payroll_reconciliation
                        (payroll_run_id, expected_total, actual_total, status)
                    VALUES (:rid, 100000, 100000, 'MISMATCH')
                """),
                {"rid": run_id},
            )
            db.commit()
    finally:
        db.rollback()
        db.close()
