"""
Regression tests: PATCH /{workspace_id}/component-overrides/{component_code}

INVARIANT PROTECTED (T4.1 — critical, money):
    A PATCH payload that omits `overrides_json` must NOT destroy the stored
    overrides_json on an existing client_component_metadata row.

    Root cause history: the original ON CONFLICT DO UPDATE unconditionally
    wrote EXCLUDED.overrides_json, so a UI call that only toggled is_active
    (or set proration_strategy) silently wiped configured NHF / Health
    Insurance / Development Levy rates for the workspace. The fix is the
    `CASE WHEN :has_overrides` guard in workspace.py::patch_component_override.
    These tests fail if that guard is ever removed.

Requirements
------------
- PostgreSQL running at DATABASE_URL env var (same as the rest of the suite).
"""

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.api.main import app
from backend.infra.db.models import Account, Workspace
from backend.infra.db.session import SessionLocal

client = TestClient(app)

COMPONENT_CODE = "T41_OVERRIDE_COMP"
ORIGINAL_OVERRIDES = {"employee_rate": 0.025, "flat_amount": 5000}


def _setup(db, account_id, workspace_id, component_metadata_id):
    db.add(Account(account_id=account_id, name="Override Patch Test Corp"))
    db.add(Workspace(
        workspace_id=workspace_id,
        account_id=account_id,
        name="Override Patch Test Workspace",
        country_code="NG",
        base_currency="NGN",
        status="DRAFT",
    ))
    # The PATCH route validates component_code against component_metadata for
    # the workspace's country — register a dedicated test code.
    db.execute(
        text("""
            INSERT INTO component_metadata
                (component_metadata_id, component_code, country_code, version,
                 metadata_json, effective_from, is_active)
            VALUES (:cm_id, :code, 'NG', 9041, '{}', CURRENT_DATE, true)
        """),
        {"cm_id": component_metadata_id, "code": COMPONENT_CODE},
    )
    db.commit()


def _cleanup(db, account_id, workspace_id, component_metadata_id):
    db.rollback()
    db.execute(
        text("DELETE FROM client_component_metadata WHERE workspace_id = :wid"),
        {"wid": workspace_id},
    )
    db.execute(
        text("DELETE FROM component_metadata WHERE component_metadata_id = :cm_id"),
        {"cm_id": component_metadata_id},
    )
    db.execute(text("DELETE FROM workspace WHERE workspace_id = :wid"), {"wid": workspace_id})
    db.execute(text("DELETE FROM account WHERE account_id = :aid"), {"aid": account_id})
    db.commit()
    db.close()


def _fetch_override_row(db, workspace_id):
    return db.execute(
        text("""
            SELECT overrides_json, is_active, proration_strategy
            FROM client_component_metadata
            WHERE workspace_id = :wid AND component_code = :code
        """),
        {"wid": workspace_id, "code": COMPONENT_CODE},
    ).fetchone()


def test_patch_without_overrides_json_preserves_existing_overrides():
    """is_active-only PATCH must leave overrides_json untouched."""
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    component_metadata_id = uuid.uuid4()
    db = SessionLocal()
    try:
        _setup(db, account_id, workspace_id, component_metadata_id)

        # Seed the row through the endpoint itself (create path).
        create_resp = client.patch(
            f"/api/v1/{workspace_id}/component-overrides/{COMPONENT_CODE}",
            json={"overrides_json": ORIGINAL_OVERRIDES, "is_active": True},
        )
        assert create_resp.status_code == 200, create_resp.text

        # The regression scenario: toggle is_active WITHOUT sending overrides_json.
        toggle_resp = client.patch(
            f"/api/v1/{workspace_id}/component-overrides/{COMPONENT_CODE}",
            json={"is_active": False},
        )
        assert toggle_resp.status_code == 200, toggle_resp.text

        row = _fetch_override_row(db, workspace_id)
        assert row is not None
        assert row[0] == ORIGINAL_OVERRIDES, (
            f"overrides_json was destroyed by an is_active-only PATCH: {row[0]}"
        )
        assert row[1] is False
    finally:
        _cleanup(db, account_id, workspace_id, component_metadata_id)


def test_patch_without_overrides_json_preserves_on_proration_change():
    """proration_strategy-only PATCH must leave overrides_json untouched."""
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    component_metadata_id = uuid.uuid4()
    db = SessionLocal()
    try:
        _setup(db, account_id, workspace_id, component_metadata_id)

        create_resp = client.patch(
            f"/api/v1/{workspace_id}/component-overrides/{COMPONENT_CODE}",
            json={"overrides_json": ORIGINAL_OVERRIDES},
        )
        assert create_resp.status_code == 200, create_resp.text

        proration_resp = client.patch(
            f"/api/v1/{workspace_id}/component-overrides/{COMPONENT_CODE}",
            json={"proration_strategy": "work_days"},
        )
        assert proration_resp.status_code == 200, proration_resp.text

        row = _fetch_override_row(db, workspace_id)
        assert row is not None
        assert row[0] == ORIGINAL_OVERRIDES, (
            f"overrides_json was destroyed by a proration-only PATCH: {row[0]}"
        )
        assert row[2] == "work_days"
    finally:
        _cleanup(db, account_id, workspace_id, component_metadata_id)


def test_patch_with_overrides_json_replaces_them():
    """Sending overrides_json explicitly must still replace the stored value."""
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    component_metadata_id = uuid.uuid4()
    db = SessionLocal()
    try:
        _setup(db, account_id, workspace_id, component_metadata_id)

        client.patch(
            f"/api/v1/{workspace_id}/component-overrides/{COMPONENT_CODE}",
            json={"overrides_json": ORIGINAL_OVERRIDES},
        )

        new_overrides = {"employee_rate": 0.03}
        update_resp = client.patch(
            f"/api/v1/{workspace_id}/component-overrides/{COMPONENT_CODE}",
            json={"overrides_json": new_overrides},
        )
        assert update_resp.status_code == 200, update_resp.text

        row = _fetch_override_row(db, workspace_id)
        assert row[0] == new_overrides
    finally:
        _cleanup(db, account_id, workspace_id, component_metadata_id)
