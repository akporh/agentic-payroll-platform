from backend.domain.payroll.calculator import calculate_net_pay

def test_calculate_net_pay():
    bands = [
        {"lower_limit": 0, "upper_limit": 300000, "rate": 0.07},
        {"lower_limit": 300000, "upper_limit": 600000, "rate": 0.11},
        {"lower_limit": 600000, "upper_limit": None, "rate": 0.15},
    ]

    result = calculate_net_pay(800000, bands)

    assert result["paye"] == 84000
    assert result["net"] == 716000
