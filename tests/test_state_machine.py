import pytest
from backend.domain.payroll.status import PayrollRunStatus
from backend.domain.payroll.state_machine import can_transition, transition


def test_valid_draft_to_calculating():
    assert can_transition(PayrollRunStatus.DRAFT, PayrollRunStatus.CALCULATING) is True
    result = transition(PayrollRunStatus.DRAFT, PayrollRunStatus.CALCULATING)
    assert result is PayrollRunStatus.CALCULATING


def test_valid_calculating_to_calculated():
    assert can_transition(PayrollRunStatus.CALCULATING, PayrollRunStatus.CALCULATED) is True
    result = transition(PayrollRunStatus.CALCULATING, PayrollRunStatus.CALCULATED)
    assert result is PayrollRunStatus.CALCULATED


def test_invalid_draft_to_calculated_skip():
    assert can_transition(PayrollRunStatus.DRAFT, PayrollRunStatus.CALCULATED) is False
    with pytest.raises(ValueError):
        transition(PayrollRunStatus.DRAFT, PayrollRunStatus.CALCULATED)


def test_invalid_locked_to_approved_backwards():
    assert can_transition(PayrollRunStatus.LOCKED, PayrollRunStatus.APPROVED) is False
    with pytest.raises(ValueError):
        transition(PayrollRunStatus.LOCKED, PayrollRunStatus.APPROVED)
