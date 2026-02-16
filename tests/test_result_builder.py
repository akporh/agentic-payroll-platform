from backend.domain.payroll.result_builder import build_payroll_result


COMPONENTS = [
    {"code": "BASIC", "amount": 500000},
    {"code": "HOUSING", "amount": 300000},
]

TAX_BANDS = [
    {"lower_limit": 0, "upper_limit": 300000, "rate": 0.07},
    {"lower_limit": 300000, "upper_limit": 600000, "rate": 0.11},
    {"lower_limit": 600000, "upper_limit": None, "rate": 0.15},
]


def test_build_payroll_result():
    result = build_payroll_result(COMPONENTS, TAX_BANDS)
    assert result["gross_components_jsonb"] == COMPONENTS
    assert result["deductions_jsonb"] == {"PAYE": 84000.0}
    assert result["net_pay"] == 716000.0
    assert result["calculations_snapshot_json"] == {
        "gross": 800000.0,
        "paye": 84000.0,
        "net": 716000.0,
    }
