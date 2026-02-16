from backend.domain.payroll.salary import calculate_gross


def test_gross_from_components():
    components = [
        {"code": "BASIC", "amount": 500000},
        {"code": "HOUSING", "amount": 300000},
    ]
    result = calculate_gross(components)
    assert result == 800000.0
