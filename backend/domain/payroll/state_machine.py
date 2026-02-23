"""
Payroll Run State Machine.

Enforces the strict, linear state transition rules for PAYROLL_RUN records.
Transitions must follow: DRAFT → CALCULATING → CALCULATED → APPROVED → LOCKED.
No skipping states. No backwards movement.

This is a pure deterministic module with no database dependencies.

Reference: ARCHITECTURE_LOCK.md — State Transitions (Locked).
"""

from backend.domain.payroll.status import PayrollRunStatus

ALLOWED_TRANSITIONS: dict[PayrollRunStatus, list[PayrollRunStatus]] = {
    PayrollRunStatus.DRAFT: [PayrollRunStatus.CALCULATING],
    PayrollRunStatus.CALCULATING: [PayrollRunStatus.CALCULATED, PayrollRunStatus.PARTIAL],
    PayrollRunStatus.PARTIAL: [PayrollRunStatus.CALCULATED],
    PayrollRunStatus.CALCULATED: [PayrollRunStatus.APPROVED],
    PayrollRunStatus.APPROVED: [PayrollRunStatus.LOCKED],
    PayrollRunStatus.LOCKED: [],
}
"""Maps each status to its list of valid next statuses."""


def can_transition(current: PayrollRunStatus, next: PayrollRunStatus) -> bool:
    """Check whether a state transition is allowed.

    Args:
        current: The current status of the payroll run.
        next: The proposed new status.

    Returns:
        True if the transition is valid, False otherwise.
    """
    return next in ALLOWED_TRANSITIONS.get(current, [])


def transition(current: PayrollRunStatus, next: PayrollRunStatus) -> PayrollRunStatus:
    """Execute a state transition, raising on invalid moves.

    Args:
        current: The current status of the payroll run.
        next: The proposed new status.

    Returns:
        The new status if the transition is valid.

    Raises:
        ValueError: If the transition violates the allowed state machine rules.
            The error message includes the current state and its allowed targets.
    """
    if not can_transition(current, next):
        raise ValueError(
            f"Invalid transition: {current.value} → {next.value}. "
            f"Allowed from {current.value}: {[s.value for s in ALLOWED_TRANSITIONS.get(current, [])]}"
        )
    return next
