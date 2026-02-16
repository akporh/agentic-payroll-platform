from backend.domain.payroll.executor import execute_single_employee_payroll


COMPONENTS = [
    {"code": "BASIC", "amount": 500000},
    {"code": "HOUSING", "amount": 300000},
]

TAX_BANDS = [
    {"lower_limit": 0, "upper_limit": 300000, "rate": 0.07},
    {"lower_limit": 300000, "upper_limit": 600000, "rate": 0.11},
    {"lower_limit": 600000, "upper_limit": None, "rate": 0.15},
]


def test_execute_single_employee_payroll():
    result = execute_single_employee_payroll(
        payroll_run_id="run1",
        employee_id="emp1",
        components=COMPONENTS,
        tax_bands=TAX_BANDS,
        statutory_rule_id="rule2026",
        statutory_version=1,
        payroll_rule_ids=["r1"],
        performed_by="admin@test.com",
    )
    assert result["payroll_run_id"] == "run1"
    assert result["employee_id"] == "emp1"
    assert result["payroll_result"]["net_pay"] == 716000.0
    assert result["rules_context_snapshot"]["statutory_rule"]["id"] == "rule2026"
    assert result["rules_context_snapshot"]["statutory_rule"]["version"] == 1
