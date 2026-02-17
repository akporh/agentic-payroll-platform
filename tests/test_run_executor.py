from backend.domain.payroll.run_executor import execute_payroll_run_pure


EMPLOYEES = [
    {
        "employee_id": "emp1",
        "components": [
            {"code": "BASIC", "amount": 500000},
            {"code": "HOUSING", "amount": 300000},
        ],
    },
    {
        "employee_id": "emp2",
        "components": [
            {"code": "BASIC", "amount": 500000},
            {"code": "HOUSING", "amount": 300000},
        ],
    },
]

TAX_BANDS = [
    {"lower_limit": 0, "upper_limit": 300000, "rate": 0.07},
    {"lower_limit": 300000, "upper_limit": 600000, "rate": 0.11},
    {"lower_limit": 600000, "upper_limit": None, "rate": 0.15},
]


def test_execute_payroll_run_pure():
    result = execute_payroll_run_pure(
        payroll_run_id="run1",
        workspace_id="ws1",
        employees=EMPLOYEES,
        tax_bands=TAX_BANDS,
        statutory_rule_id="rule2026",
        statutory_version=1,
        payroll_rule_ids=["r1"],
        performed_by="admin@test.com",
    )
    assert result["payroll_run_id"] == "run1"
    assert len(result["results"]) == 2
    assert result["totals"]["total_net_pay"] == 1432000.0
    assert len(result["audit_logs"]) == 2
    assert len(result["events"]) == 2
