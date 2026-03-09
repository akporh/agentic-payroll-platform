import uuid
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.api.main import app

client = TestClient(app)

MOCK_WORKSPACE_ID = str(uuid.uuid4())
MOCK_WORKSPACE_NAME = "Test Workspace"


# ---------------------------------------------------------------------------
# GET /api/v1/workspace/info
# ---------------------------------------------------------------------------

def test_workspace_info_no_workspace():
    """Returns safe defaults when no workspace row exists."""
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchone.return_value = None

    with patch("backend.api.routes.workspace.SessionLocal", return_value=mock_db):
        response = client.get("/api/v1/workspace/info")

    assert response.status_code == 200
    body = response.json()
    assert body["workspace_name"] == "Not Found"
    assert body["active_employee_count"] == 0


def test_workspace_info_workspace_exists():
    """Returns workspace details and employee count when a row is present."""
    workspace_call = MagicMock()
    workspace_call.fetchone.return_value = (MOCK_WORKSPACE_ID, MOCK_WORKSPACE_NAME)

    count_call = MagicMock()
    count_call.scalar.return_value = 3

    mock_db = MagicMock()
    mock_db.execute.side_effect = [workspace_call, count_call]

    with patch("backend.api.routes.workspace.SessionLocal", return_value=mock_db):
        response = client.get("/api/v1/workspace/info")

    assert response.status_code == 200
    body = response.json()
    assert body["workspace_id"] == MOCK_WORKSPACE_ID
    assert body["workspace_name"] == MOCK_WORKSPACE_NAME
    assert body["active_employee_count"] == 3


# ---------------------------------------------------------------------------
# POST /api/v1/{workspace_id}/designation
# ---------------------------------------------------------------------------

def test_create_designation_success():
    """Valid payload returns 200 and the created designation."""
    mock_result = MagicMock()
    mock_result.designation_id = str(uuid.uuid4())
    mock_result.workspace_id = MOCK_WORKSPACE_ID
    mock_result.designation_code = "ENG"
    mock_result.description = "Engineering"

    mock_db = MagicMock()

    with patch("backend.api.routes.workspace.SessionLocal", return_value=mock_db), \
         patch("backend.api.routes.workspace.onboarding_service.create_designation", return_value=mock_result):
        response = client.post(
            f"/api/v1/{MOCK_WORKSPACE_ID}/designation",
            json={"designation_code": "ENG", "description": "Engineering"},
        )

    assert response.status_code == 200


def test_create_designation_without_description():
    """description is optional — omitting it should still return 200."""
    mock_result = MagicMock()
    mock_result.designation_id = str(uuid.uuid4())
    mock_result.workspace_id = MOCK_WORKSPACE_ID
    mock_result.designation_code = "MGR"
    mock_result.description = None

    mock_db = MagicMock()

    with patch("backend.api.routes.workspace.SessionLocal", return_value=mock_db), \
         patch("backend.api.routes.workspace.onboarding_service.create_designation", return_value=mock_result):
        response = client.post(
            f"/api/v1/{MOCK_WORKSPACE_ID}/designation",
            json={"designation_code": "MGR"},
        )

    assert response.status_code == 200


def test_create_designation_missing_required_field():
    """Omitting designation_code returns 422 Unprocessable Entity."""
    response = client.post(
        f"/api/v1/{MOCK_WORKSPACE_ID}/designation",
        json={"description": "No code provided"},
    )

    assert response.status_code == 422
