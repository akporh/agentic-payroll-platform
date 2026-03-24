from decimal import Decimal
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
    # gross_components_jsonb is a dict keyed by component code
    assert result["gross_components_jsonb"] == {
        "BASIC":   {"amount": 500000},
        "HOUSING": {"amount": 300000},
    }
    assert result["deductions_jsonb"] == {"PAYE": Decimal("84000.00")}
    assert result["net_pay"] == Decimal("716000.00")
    assert result["calculations_snapshot_json"] == {
        "gross": Decimal("800000"),
        "paye": Decimal("84000.00"),
        "net": Decimal("716000.00"),
    }
