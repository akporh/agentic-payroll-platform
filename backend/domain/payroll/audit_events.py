"""
Audit and Event Payload Builders for PAYROLL_RUN Transitions.

Generates deterministic audit_log and event_store payloads when a
PAYROLL_RUN status changes. These dicts are shaped to match the
Phase 1 audit_log and event_store table schemas.

No database writes — payload construction only.

Reference: ARCHITECTURE_LOCK.md — Audit Requirements.
"""

from backend.domain.payroll.status import PayrollRunStatus


def build_transition_audit(
    payroll_run_id: str,
    old_status: PayrollRunStatus,
    new_status: PayrollRunStatus,
    performed_by: str,
) -> dict:
    """Build an audit_log payload for a payroll run status transition.

    Args:
        payroll_run_id: Unique identifier of the payroll run.
        old_status: Status before the transition.
        new_status: Status after the transition.
        performed_by: Identifier of the user or system that triggered the change.

    Returns:
        Dict matching the audit_log table schema with old and new status values.
    """
    return {
        "entity_type": "PAYROLL_RUN",
        "entity_id": payroll_run_id,
        "action": "STATUS_TRANSITION",
        "old_value_jsonb": {"status": old_status.value},
        "new_value_jsonb": {"status": new_status.value},
        "performed_by": performed_by,
    }


def build_transition_event(
    payroll_run_id: str,
    old_status: PayrollRunStatus,
    new_status: PayrollRunStatus,
) -> dict:
    """Build an event_store payload for a payroll run status transition.

    Args:
        payroll_run_id: Unique identifier of the payroll run.
        old_status: Status before the transition.
        new_status: Status after the transition.

    Returns:
        Dict matching the event_store table schema with the transition details
        captured in the event_payload.
    """
    return {
        "aggregate_type": "PAYROLL_RUN",
        "aggregate_id": payroll_run_id,
        "event_type": "PAYROLL_RUN_STATUS_CHANGED",
        "event_payload": {
            "from": old_status.value,
            "to": new_status.value,
        },
    }
