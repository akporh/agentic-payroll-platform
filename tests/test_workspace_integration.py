import uuid

from fastapi.testclient import TestClient

from backend.api.main import app
from backend.infra.db.session import SessionLocal
from backend.infra.db.models import Workspace, Designation

client = TestClient(app)


def test_workspace_info_returns_workspace_details():
    """
    GET /api/v1/workspace/info returns full workspace details when a workspace exists.
    Creates one for the duration of the test, then removes it.
    """
    db = SessionLocal()
    workspace_id = uuid.uuid4()

    try:
        db.add(Workspace(
            workspace_id=workspace_id,
            name="Integration Test Workspace",
            country_code="NG",
            base_currency="NGN",
            status="DRAFT",
        ))
        db.commit()

        response = client.get("/api/v1/workspace/info")

        assert response.status_code == 200
        body = response.json()
        assert "workspace_name" in body
        assert "active_employee_count" in body
        assert "workspace_id" in body  # only present when a workspace exists

    finally:
        db.query(Designation).filter_by(workspace_id=workspace_id).delete()
        db.query(Workspace).filter_by(workspace_id=workspace_id).delete()
        db.commit()
        db.close()


def test_create_designation_persists_to_db():
    """
    POST /{workspace_id}/designation writes a row to the designation table.
    Verified by querying the DB directly after the endpoint responds.
    """
    db = SessionLocal()
    workspace_id = uuid.uuid4()

    try:
        db.add(Workspace(
            workspace_id=workspace_id,
            name="Integration Test Workspace",
            country_code="NG",
            base_currency="NGN",
            status="DRAFT",
        ))
        db.commit()

        response = client.post(
            f"/api/v1/{workspace_id}/designation",
            json={"designation_code": "INT-ENG", "description": "Integration Engineering"},
        )

        assert response.status_code == 200

        # Query the DB directly — no mocks, no endpoint, raw session
        saved = db.query(Designation).filter_by(
            workspace_id=workspace_id,
            designation_code="INT-ENG",
        ).first()

        assert saved is not None
        assert saved.designation_code == "INT-ENG"
        assert saved.description == "Integration Engineering"
        assert saved.workspace_id == workspace_id

    finally:
        db.query(Designation).filter_by(workspace_id=workspace_id).delete()
        db.query(Workspace).filter_by(workspace_id=workspace_id).delete()
        db.commit()
        db.close()
