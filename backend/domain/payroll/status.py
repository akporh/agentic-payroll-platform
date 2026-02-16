from enum import Enum


class PayrollRunStatus(Enum):
    DRAFT = "DRAFT"
    CALCULATING = "CALCULATING"
    CALCULATED = "CALCULATED"
    APPROVED = "APPROVED"
    LOCKED = "LOCKED"
