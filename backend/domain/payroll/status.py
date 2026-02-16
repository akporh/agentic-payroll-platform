"""
Payroll Run Status Enum.

Defines the single source of truth for all valid PAYROLL_RUN lifecycle
statuses. The order of members reflects the required progression:
DRAFT → CALCULATING → CALCULATED → APPROVED → LOCKED.

No state may be skipped. See state_machine.py for transition enforcement.

Reference: ARCHITECTURE_LOCK.md — State Transitions (Locked).
"""

from enum import Enum


class PayrollRunStatus(Enum):
    """Valid lifecycle statuses for a payroll run.

    Members (in required order):
        DRAFT: Initial state. Run is being prepared.
        CALCULATING: Payroll engine is actively computing results.
        CALCULATED: All calculations complete, awaiting review.
        APPROVED: Authorized approver has signed off on results.
        LOCKED: Finalized and immutable. No further changes allowed.
    """

    DRAFT = "DRAFT"
    CALCULATING = "CALCULATING"
    CALCULATED = "CALCULATED"
    APPROVED = "APPROVED"
    LOCKED = "LOCKED"
