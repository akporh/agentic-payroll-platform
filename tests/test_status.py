from backend.domain.payroll.status import PayrollRunStatus


def test_enum_has_expected_values():
    expected = {"DRAFT", "CALCULATING", "CALCULATED", "APPROVED", "LOCKED", "PARTIAL", "PAID"}
    actual = {s.value for s in PayrollRunStatus}
    assert actual == expected


def test_enum_contains_expected_values():
    expected = {"DRAFT", "CALCULATING", "CALCULATED", "APPROVED", "LOCKED", "PARTIAL", "PAID"}
    actual = {s.value for s in PayrollRunStatus}
    assert actual == expected


def test_draft_is_initial_status():
    statuses = list(PayrollRunStatus)
    assert statuses[0] is PayrollRunStatus.DRAFT
