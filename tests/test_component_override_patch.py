"""
Regression tests: PATCH /{workspace_id}/component-overrides/{component_code}

INVARIANT PROTECTED (T4.1 — critical, money):
    A PATCH payload that omits `overrides_json` must NOT destroy the stored
    overrides_json on an existing client_component_metadata row.

    Root cause history: the original ON CONFLICT DO UPDATE unconditionally
    wrote EXCLUDED.overrides_json, so a UI call that only toggled is_active
    (or set proration_strategy) silently wiped configured NHF / Health
    Insurance / Development Levy rates for the workspace. The fix is that
    overrides_json is now merged into the existing value key-by-key, never
    replaced wholesale, in workspace.py::patch_component_override.

INVARIANT PROTECTED (dev-levy-rule-pct, Story 1 — merge-not-replace):
    A PATCH that sends overrides_json carrying only the key(s) being changed
    must merge into the existing overrides_json, not replace it wholesale.
    This was the actual failure mode the DEVELOPMENT_LEVY Edit Override
    SlideOver would have hit: an amount-only PATCH would have silently
    destroyed a previously-set component_class/flat_amount key. These tests
    fail if the merge behaviour is ever reverted to a wholesale replace.

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


LEVY_COMPONENT_CODE = "T41_LEVY_OVERRIDE_COMP"


def _setup(db, account_id, workspace_id, component_metadata_id, code=COMPONENT_CODE, metadata_json="{}"):
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
            VALUES (:cm_id, :code, 'NG', 9041, CAST(:meta AS jsonb), CURRENT_DATE, true)
        """),
        {"cm_id": component_metadata_id, "code": code, "meta": metadata_json},
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


def _fetch_override_row(db, workspace_id, code=COMPONENT_CODE):
    return db.execute(
        text("""
            SELECT overrides_json, is_active, proration_strategy
            FROM client_component_metadata
            WHERE workspace_id = :wid AND component_code = :code
        """),
        {"wid": workspace_id, "code": code},
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


def test_patch_with_overrides_json_merges_not_replaces():
    """Sending overrides_json with only a changed key must merge, not replace."""
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

        # Only employee_rate changes; flat_amount is not resent.
        update_resp = client.patch(
            f"/api/v1/{workspace_id}/component-overrides/{COMPONENT_CODE}",
            json={"overrides_json": {"employee_rate": 0.03}},
        )
        assert update_resp.status_code == 200, update_resp.text

        row = _fetch_override_row(db, workspace_id)
        assert row[0] == {"employee_rate": 0.03, "flat_amount": 5000}, (
            f"overrides_json was replaced wholesale instead of merged: {row[0]}"
        )
    finally:
        _cleanup(db, account_id, workspace_id, component_metadata_id)


def test_patch_overrides_json_new_key_does_not_disturb_unrelated_key():
    """A DEVELOPMENT_LEVY-shaped override save must not disturb an unrelated
    component_class/flat_amount key already stored for this component.

    Regression for docs/sprints/dev-levy-rule-pct/plan.md Story 1 AC:
    "PATCH on any other component's overrides_json ... is unaffected by an
    unrelated DEVELOPMENT_LEVY override save on the same workspace."
    """
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    component_metadata_id = uuid.uuid4()
    db = SessionLocal()
    try:
        _setup(db, account_id, workspace_id, component_metadata_id)

        client.patch(
            f"/api/v1/{workspace_id}/component-overrides/{COMPONENT_CODE}",
            json={"overrides_json": {"component_class": "non_taxable", "flat_amount": 5000}},
        )

        update_resp = client.patch(
            f"/api/v1/{workspace_id}/component-overrides/{COMPONENT_CODE}",
            json={"overrides_json": {"annual_amount": 150}},
        )
        assert update_resp.status_code == 200, update_resp.text

        row = _fetch_override_row(db, workspace_id)
        assert row[0] == {
            "component_class": "non_taxable",
            "flat_amount": 5000,
            "annual_amount": 150,
        }
    finally:
        _cleanup(db, account_id, workspace_id, component_metadata_id)


_LEVY_METADATA_JSON = '{"engine_behavior": {"workspace_override_key": "annual_amount"}}'


def test_patch_null_value_deletes_key_reverting_to_default():
    """An explicit `null` for a key clears a previously-set override.

    Under merge-not-replace, omitting a key from the payload can no longer
    clear a stale value (the merge just keeps it) — null is the delete
    sentinel the UI's "leave blank to use the statutory default" relies on.
    """
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    component_metadata_id = uuid.uuid4()
    db = SessionLocal()
    try:
        _setup(db, account_id, workspace_id, component_metadata_id,
               code=LEVY_COMPONENT_CODE, metadata_json=_LEVY_METADATA_JSON)

        client.patch(
            f"/api/v1/{workspace_id}/component-overrides/{LEVY_COMPONENT_CODE}",
            json={"overrides_json": {"annual_amount": 150}},
        )

        clear_resp = client.patch(
            f"/api/v1/{workspace_id}/component-overrides/{LEVY_COMPONENT_CODE}",
            json={"overrides_json": {"annual_amount": None}},
        )
        assert clear_resp.status_code == 200, clear_resp.text

        row = _fetch_override_row(db, workspace_id, code=LEVY_COMPONENT_CODE)
        assert row[0] == {}
    finally:
        _cleanup(db, account_id, workspace_id, component_metadata_id)


def test_patch_rejects_non_numeric_override_amount():
    """PATCH with a non-numeric annual_amount -> 422, no exception string leaked."""
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    component_metadata_id = uuid.uuid4()
    db = SessionLocal()
    try:
        _setup(db, account_id, workspace_id, component_metadata_id,
               code=LEVY_COMPONENT_CODE, metadata_json=_LEVY_METADATA_JSON)

        resp = client.patch(
            f"/api/v1/{workspace_id}/component-overrides/{LEVY_COMPONENT_CODE}",
            json={"overrides_json": {"annual_amount": "not-a-number"}},
        )
        assert resp.status_code == 422, resp.text
        assert "not-a-number" not in resp.text
        assert "Traceback" not in resp.text
    finally:
        _cleanup(db, account_id, workspace_id, component_metadata_id)


def test_patch_rejects_negative_override_amount():
    """PATCH with a negative annual_amount -> 422."""
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    component_metadata_id = uuid.uuid4()
    db = SessionLocal()
    try:
        _setup(db, account_id, workspace_id, component_metadata_id,
               code=LEVY_COMPONENT_CODE, metadata_json=_LEVY_METADATA_JSON)

        resp = client.patch(
            f"/api/v1/{workspace_id}/component-overrides/{LEVY_COMPONENT_CODE}",
            json={"overrides_json": {"annual_amount": -100}},
        )
        assert resp.status_code == 422, resp.text
    finally:
        _cleanup(db, account_id, workspace_id, component_metadata_id)


def test_patch_accepts_explicit_zero_override_amount():
    """An explicit annual_amount: 0 is a valid override, distinct from absent."""
    account_id            = uuid.uuid4()
    workspace_id          = uuid.uuid4()
    component_metadata_id = uuid.uuid4()
    db = SessionLocal()
    try:
        _setup(db, account_id, workspace_id, component_metadata_id,
               code=LEVY_COMPONENT_CODE, metadata_json=_LEVY_METADATA_JSON)

        resp = client.patch(
            f"/api/v1/{workspace_id}/component-overrides/{LEVY_COMPONENT_CODE}",
            json={"overrides_json": {"annual_amount": 0}},
        )
        assert resp.status_code == 200, resp.text

        row = _fetch_override_row(db, workspace_id, code=LEVY_COMPONENT_CODE)
        assert row[0] == {"annual_amount": 0}
    finally:
        _cleanup(db, account_id, workspace_id, component_metadata_id)
