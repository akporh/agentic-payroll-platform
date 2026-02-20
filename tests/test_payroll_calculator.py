from decimal import Decimal
from backend.domain.payroll.calculator import calculate_net_pay


TAX_BANDS = [
    {"lower_limit": 0, "upper_limit": 300000, "rate": 0.07},
    {"lower_limit": 300000, "upper_limit": 600000, "rate": 0.11},
    {"lower_limit": 600000, "upper_limit": None, "rate": 0.15},
]


def test_net_pay_800000():
    result = calculate_net_pay(Decimal("800000"), TAX_BANDS)
    assert result["gross"] == Decimal("800000")
    assert result["paye"] == Decimal("84000.00")
    assert result["net"] == Decimal("716000.00")
