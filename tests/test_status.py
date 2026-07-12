from backend.domain.payroll.status import PayrollRunStatus


def test_enum_has_expected_values():
    # FAILED added by 05-001 remediation — a calculation precondition (e.g.
    # snapshot creation) that fails before calculation begins now leaves an
    # operator-visible terminal status instead of an indistinguishable DRAFT.
    expected = {"DRAFT", "FAILED", "CALCULATING", "CALCULATED", "APPROVED", "LOCKED", "PARTIAL", "PAID"}
    actual = {s.value for s in PayrollRunStatus}
    assert actual == expected


def test_enum_contains_expected_values():
    # FAILED added by 05-001 remediation — a calculation precondition (e.g.
    # snapshot creation) that fails before calculation begins now leaves an
    # operator-visible terminal status instead of an indistinguishable DRAFT.
    expected = {"DRAFT", "FAILED", "CALCULATING", "CALCULATED", "APPROVED", "LOCKED", "PARTIAL", "PAID"}
    actual = {s.value for s in PayrollRunStatus}
    assert actual == expected


def test_draft_is_initial_status():
    statuses = list(PayrollRunStatus)
    assert statuses[0] is PayrollRunStatus.DRAFT
