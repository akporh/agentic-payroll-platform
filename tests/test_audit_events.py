from backend.domain.payroll.status import PayrollRunStatus
from backend.domain.payroll.audit_events import (
    build_transition_audit,
    build_transition_event,
)


def test_build_transition_audit():
    audit = build_transition_audit(
        payroll_run_id="run123",
        old_status=PayrollRunStatus.DRAFT,
        new_status=PayrollRunStatus.CALCULATING,
        performed_by="admin_user",
    )
    assert audit["entity_type"] == "PAYROLL_RUN"
    assert audit["entity_id"] == "run123"
    assert audit["action"] == "STATUS_TRANSITION"
    assert audit["old_value_jsonb"] == {"status": "DRAFT"}
    assert audit["new_value_jsonb"] == {"status": "CALCULATING"}
    assert audit["performed_by"] == "admin_user"


def test_build_transition_event():
    event = build_transition_event(
        payroll_run_id="run123",
        old_status=PayrollRunStatus.DRAFT,
        new_status=PayrollRunStatus.CALCULATING,
    )
    assert event["aggregate_type"] == "PAYROLL_RUN"
    assert event["aggregate_id"] == "run123"
    assert event["event_type"] == "PAYROLL_RUN_STATUS_CHANGED"
    assert event["event_payload"]["from"] == "DRAFT"
    assert event["event_payload"]["to"] == "CALCULATING"
