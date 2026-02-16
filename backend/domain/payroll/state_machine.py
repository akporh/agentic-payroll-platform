from backend.domain.payroll.status import PayrollRunStatus

ALLOWED_TRANSITIONS = {
    PayrollRunStatus.DRAFT: [PayrollRunStatus.CALCULATING],
    PayrollRunStatus.CALCULATING: [PayrollRunStatus.CALCULATED],
    PayrollRunStatus.CALCULATED: [PayrollRunStatus.APPROVED],
    PayrollRunStatus.APPROVED: [PayrollRunStatus.LOCKED],
    PayrollRunStatus.LOCKED: [],
}


def can_transition(current: PayrollRunStatus, next: PayrollRunStatus) -> bool:
    return next in ALLOWED_TRANSITIONS.get(current, [])


def transition(current: PayrollRunStatus, next: PayrollRunStatus) -> PayrollRunStatus:
    if not can_transition(current, next):
        raise ValueError(
            f"Invalid transition: {current.value} → {next.value}. "
            f"Allowed from {current.value}: {[s.value for s in ALLOWED_TRANSITIONS.get(current, [])]}"
        )
    return next
