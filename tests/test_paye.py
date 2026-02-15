from backend.domain.rules.paye import calculate_paye


TAX_BANDS = [
    {"lower_limit": 0, "upper_limit": 300000, "rate": 0.07},
    {"lower_limit": 300000, "upper_limit": 600000, "rate": 0.11},
    {"lower_limit": 600000, "upper_limit": None, "rate": 0.15},
]


def test_paye_800000():
    result = calculate_paye(800000, TAX_BANDS)
    assert result == 84000.0


def test_paye_zero_income():
    result = calculate_paye(0, TAX_BANDS)
    assert result == 0.0


def test_paye_within_first_band():
    result = calculate_paye(100000, TAX_BANDS)
    assert result == 7000.0


def test_paye_at_first_boundary():
    result = calculate_paye(300000, TAX_BANDS)
    assert result == 21000.0


def test_paye_within_second_band():
    result = calculate_paye(450000, TAX_BANDS)
    expected = (300000 * 0.07) + (150000 * 0.11)
    assert result == expected


def test_paye_at_second_boundary():
    result = calculate_paye(600000, TAX_BANDS)
    expected = (300000 * 0.07) + (300000 * 0.11)
    assert result == expected


def test_paye_deterministic():
    r1 = calculate_paye(800000, TAX_BANDS)
    r2 = calculate_paye(800000, TAX_BANDS)
    assert r1 == r2 == 84000.0
