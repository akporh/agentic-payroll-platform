from backend.domain.payroll.calculator import calculate_net_pay


TAX_BANDS = [
    {"lower_limit": 0, "upper_limit": 300000, "rate": 0.07},
    {"lower_limit": 300000, "upper_limit": 600000, "rate": 0.11},
    {"lower_limit": 600000, "upper_limit": None, "rate": 0.15},
]


def test_net_pay_800000():
    result = calculate_net_pay(800000, TAX_BANDS)
    assert result["gross"] == 800000
    assert result["paye"] == 84000.0
    assert result["net"] == 716000.0
