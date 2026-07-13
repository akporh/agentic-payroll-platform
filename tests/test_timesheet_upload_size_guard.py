"""SEC-S7: server-side size cap on the timesheet upload endpoint.

Focused unit test — monkeypatches the workspace-config lookup and the
derivation service so only the size-guard logic in
backend/api/routes/payroll.py::upload_timesheet is under test, with no DB
fixture required.
"""
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.api.routes import payroll as payroll_routes

client = TestClient(app)

_WORKSPACE_ID = "00000000-0000-0000-0000-000000000abc"


def _enable_timesheet(monkeypatch):
    monkeypatch.setattr(
        payroll_routes._ws_cfg_repo,
        "get_workspace_payroll_config",
        lambda workspace_id: {"timesheet_enabled": True},
    )


def test_oversized_upload_rejected_with_413(monkeypatch):
    """A file over MAX_TIMESHEET_UPLOAD_BYTES is rejected before parsing."""
    _enable_timesheet(monkeypatch)

    called = {"upload_timesheet": False}

    def _fail_if_called(*args, **kwargs):
        called["upload_timesheet"] = True
        raise AssertionError("derivation service must not run for an oversized file")

    monkeypatch.setattr(payroll_routes.timesheet_derivation_service, "upload_timesheet", _fail_if_called)

    oversized = b"0" * (payroll_routes.MAX_TIMESHEET_UPLOAD_BYTES + 1)
    resp = client.post(
        f"/api/v1/workspaces/{_WORKSPACE_ID}/timesheet/upload",
        params={"period_start": "2026-06-01", "period_end": "2026-06-30"},
        files={"file": ("timesheet.xlsx", oversized, "application/octet-stream")},
    )

    assert resp.status_code == 413
    assert "too large" in resp.json()["detail"].lower()
    assert called["upload_timesheet"] is False


def test_within_limit_upload_reaches_derivation_service(monkeypatch):
    """A file at/under the limit proceeds to the derivation service unchanged."""
    _enable_timesheet(monkeypatch)

    received = {}

    def _capture(workspace_id, period_start, period_end, file_bytes):
        received["file_bytes_len"] = len(file_bytes)
        return {"status": "ok"}

    monkeypatch.setattr(payroll_routes.timesheet_derivation_service, "upload_timesheet", _capture)

    small_file = b"0" * 1024  # 1 KB — well under the 10 MB cap
    resp = client.post(
        f"/api/v1/workspaces/{_WORKSPACE_ID}/timesheet/upload",
        params={"period_start": "2026-06-01", "period_end": "2026-06-30"},
        files={"file": ("timesheet.xlsx", small_file, "application/octet-stream")},
    )

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    assert received["file_bytes_len"] == 1024
