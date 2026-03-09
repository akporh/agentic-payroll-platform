"""
Integration test: payroll_run.rules_context_snapshot is immutable.

Validates that once a payroll run is persisted the DB trigger
trg_run_snapshot_immutable (migration a1b2c3d4e5f6) prevents any
attempt to overwrite the snapshot column.

Flow
----
1. Run a full payroll via POST /payroll/run to create a CALCULATED run.
2. Read the persisted rules_context_snapshot and assert it is correct.
3. Attempt a raw SQL UPDATE that changes the snapshot to a different value.
4. Assert that the attempt raises a DB-level exception (InternalError).
5. Re-read the snapshot and confirm it is unchanged.

Requirements
------------
- PostgreSQL running at DATABASE_URL env var.
- All Alembic migrations applied (including a1b2c3d4e5f6).
- statutory_rule version=9995 is used so this test wins ORDER BY version DESC
  when the four earlier test rules (9999, 9998, 9997, 9996) are absent.

Run:
    pytest tests/test_payroll_run_snapshot_immutable.py -v
"""

import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import InternalError

from backend.api.main import app
from backend.infra.db.models import Account, ComponentMetadata, Workspace
from backend.infra.db.session import SessionLocal

client = TestClient(app)

BASIC     = 300_000
HOUSING   = 100_000
TRANSPORT =  50_000


def test_run_snapshot_is_immutable():
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    statutory_rule_id     = uuid.uuid4()
    component_metadata_id = uuid.uuid4()

    db = SessionLocal()

    try:
        # -------------------------------------------------------------------
        # STEP 1 — Prerequisites
        # -------------------------------------------------------------------
        db.add(Account(account_id=account_id, name="Snapshot Immutable Test Corp"))

        db.add(Workspace(
            workspace_id=workspace_id,
            account_id=account_id,
            name="Snapshot Immutable Test Workspace",
            country_code="NG",
            base_currency="NGN",
            retry_strategy="FULL_RUN",
            status="DRAFT",
        ))

        db.execute(
            text("""
                INSERT INTO statutory_rule (statutory_rule_id, state, version, rules_jsonb)
                VALUES (:id, 'NATIONAL', 9995, '{}')
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

        db.add(ComponentMetadata(
            component_metadata_id=component_metadata_id,
            country_code="NG",
            version=1,
            rules_jsonb={},
            effective_from=date.today(),
            is_active=True,
        ))

        db.commit()

        # -------------------------------------------------------------------
        # STEP 2 — Onboard one employee and run payroll
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
                    "full_name":              "Snapshot Test Employee",
                    "salary_definition_name": "STANDARD",
                    "biodata": {
                        "TIN":            "9988776655",
                        "BANK":           "Access Bank",
                        "ACCOUNT_NUMBER": "9876543210",
                        "RSA":            "PEN200000001",
                        "FULL_NAME":      "Snapshot Test Employee",
                    },
                }
            ],
        }

        commit_resp = client.post("/api/v1/onboarding/commit", json=onboarding_payload)
        assert commit_resp.status_code == 200, commit_resp.text

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
        payroll_run_id = payroll_resp.json()["payroll_run_id"]

        # -------------------------------------------------------------------
        # STEP 3 — Assert snapshot is correctly persisted
        # -------------------------------------------------------------------
        snapshot = db.execute(
            text("SELECT rules_context_snapshot FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": payroll_run_id},
        ).scalar()

        assert snapshot is not None, "rules_context_snapshot must not be NULL"
        assert snapshot["statutory_rule"]["id"] == str(statutory_rule_id)
        assert snapshot["statutory_rule"]["version"] == 9995
        assert isinstance(snapshot["payroll_rules"], list)

        original_snapshot = snapshot

        # -------------------------------------------------------------------
        # STEP 4 — Attempt to overwrite the snapshot — must be rejected by trigger
        # -------------------------------------------------------------------
        with pytest.raises(InternalError, match="rules_context_snapshot is immutable"):
            db.execute(
                text("""
                    UPDATE payroll_run
                    SET    rules_context_snapshot = '{"tampered": true}'::jsonb
                    WHERE  payroll_run_id = :rid
                """),
                {"rid": payroll_run_id},
            )
            db.commit()

        db.rollback()

        # -------------------------------------------------------------------
        # STEP 5 — Confirm snapshot is unchanged after the rejected update
        # -------------------------------------------------------------------
        snapshot_after = db.execute(
            text("SELECT rules_context_snapshot FROM payroll_run WHERE payroll_run_id = :rid"),
            {"rid": payroll_run_id},
        ).scalar()

        assert snapshot_after == original_snapshot, (
            f"Snapshot was modified despite trigger: {snapshot_after}"
        )

    finally:
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
