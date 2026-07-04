"""
Integration tests: date-aware payroll rule rate resolution for the Payroll
Inputs page.

Validates POST /{workspace_id}/payroll/input-codes/by-date resolves the
payroll_rule version that was actually effective as of each requested
reference date — not whichever row happens to be is_active — fixing the bug
where a historical input showed a rate that only started applying later.

Requirements
------------
- PostgreSQL running at DATABASE_URL env var.
- Alembic migrations applied.

Run:
    pytest tests/test_payroll_input_codes_route.py -v
"""

import uuid
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.api.main import app
from backend.infra.db.session import SessionLocal

client = TestClient(app)


def _insert_workspace(db, workspace_id, account_id):
    db.execute(
        text("INSERT INTO account (account_id, name) VALUES (:aid, :name)"),
        {"aid": account_id, "name": "Input Codes By Date Test Account"},
    )
    db.execute(
        text("""
            INSERT INTO workspace (workspace_id, account_id, name, country_code,
                                   base_currency, status)
            VALUES (:wid, :aid, 'Input Codes By Date Test WS', 'NG', 'NGN', 'LIVE')
        """),
        {"wid": workspace_id, "aid": account_id},
    )
    db.commit()


def _insert_rule(db, workspace_id, *, rule_name, effective_from, rate, is_active=True):
    rule_id = uuid.uuid4()
    definition = {"input_field": rule_name.lower(), "calculation_method": "unit_multiplier", "rate": rate}
    db.execute(
        text("""
            INSERT INTO payroll_rule (
                rule_id, workspace_id, rule_name, rule_definition_json,
                rule_type, is_active, effective_from
            ) VALUES (
                :rid, :wid, :name, CAST(:defn AS jsonb), 'EARNING', :active, :eff
            )
        """),
        {
            "rid": rule_id, "wid": workspace_id, "name": rule_name,
            "defn": json.dumps(definition), "active": is_active, "eff": effective_from,
        },
    )
    db.commit()
    return rule_id


def _cleanup(db, workspace_id, account_id):
    db.execute(text("DELETE FROM payroll_rule WHERE workspace_id = :wid"), {"wid": workspace_id})
    db.execute(text("DELETE FROM workspace WHERE workspace_id = :wid"), {"wid": workspace_id})
    db.execute(text("DELETE FROM account WHERE account_id = :aid"), {"aid": account_id})
    db.commit()


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_resolves_historical_rate_for_past_date(db):
    """A Dec-2025 reference date must resolve the rate effective in Dec 2025,
    not a later version that started in 2026 — the exact bug this fixes."""
    workspace_id = uuid.uuid4()
    account_id = uuid.uuid4()
    _insert_workspace(db, workspace_id, account_id)
    _insert_rule(db, workspace_id, rule_name="REGULAR_OVERTIME", effective_from="2025-01-01", rate=150)
    _insert_rule(db, workspace_id, rule_name="REGULAR_OVERTIME", effective_from="2026-01-01", rate=1000)

    try:
        resp = client.post(
            f"/api/v1/{workspace_id}/payroll/input-codes/by-date",
            json={"reference_dates": ["2025-12", "2026-07"]},
        )
        assert resp.status_code == 200
        body = resp.json()["input_codes"]

        dec_2025 = next(d for d in body["2025-12-01"] if d["rule_name"] == "REGULAR_OVERTIME")
        jul_2026 = next(d for d in body["2026-07-01"] if d["rule_name"] == "REGULAR_OVERTIME")

        assert dec_2025["rule_rate"] == 150
        assert jul_2026["rule_rate"] == 1000
    finally:
        _cleanup(db, workspace_id, account_id)


def test_empty_reference_dates_returns_empty_map(db):
    """No reference dates requested must return an empty map, not an error."""
    workspace_id = uuid.uuid4()
    account_id = uuid.uuid4()
    _insert_workspace(db, workspace_id, account_id)

    try:
        resp = client.post(
            f"/api/v1/{workspace_id}/payroll/input-codes/by-date",
            json={"reference_dates": []},
        )
        assert resp.status_code == 200
        assert resp.json() == {"input_codes": {}}
    finally:
        _cleanup(db, workspace_id, account_id)


def test_date_before_earliest_version_gets_no_match(db):
    """A reference date before any known version exists must exclude that
    rule from the bucket rather than erroring or resolving to a later rate."""
    workspace_id = uuid.uuid4()
    account_id = uuid.uuid4()
    _insert_workspace(db, workspace_id, account_id)
    _insert_rule(db, workspace_id, rule_name="SPECIAL_OVERTIME", effective_from="2025-06-01", rate=300)

    try:
        resp = client.post(
            f"/api/v1/{workspace_id}/payroll/input-codes/by-date",
            json={"reference_dates": ["2025-01"]},
        )
        assert resp.status_code == 200
        body = resp.json()["input_codes"]
        assert body["2025-01-01"] == []
    finally:
        _cleanup(db, workspace_id, account_id)
