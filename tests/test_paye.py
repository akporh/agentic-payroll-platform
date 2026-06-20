from decimal import Decimal
from backend.domain.rules.paye import calculate_paye


TAX_BANDS = [
    {"lower_limit": 0, "upper_limit": 300000, "rate": 0.07},
    {"lower_limit": 300000, "upper_limit": 600000, "rate": 0.11},
    {"lower_limit": 600000, "upper_limit": None, "rate": 0.15},
]

# Nigeria Tax Act 2025 — effective 2026-01-01
NTA_2025_BANDS = [
    {"lower_limit": 0,          "upper_limit": 800_000,    "rate": "0.00"},
    {"lower_limit": 800_000,    "upper_limit": 3_000_000,  "rate": "0.15"},
    {"lower_limit": 3_000_000,  "upper_limit": 12_000_000, "rate": "0.18"},
    {"lower_limit": 12_000_000, "upper_limit": 25_000_000, "rate": "0.21"},
    {"lower_limit": 25_000_000, "upper_limit": 50_000_000, "rate": "0.23"},
    {"lower_limit": 50_000_000, "upper_limit": None,       "rate": "0.25"},
]


def test_paye_800000():
    result = calculate_paye(800000, TAX_BANDS)
    assert result == Decimal("84000.00")


def test_paye_zero_income():
    result = calculate_paye(0, TAX_BANDS)
    assert result == Decimal("0.00")


def test_paye_within_first_band():
    result = calculate_paye(100000, TAX_BANDS)
    assert result == Decimal("7000.00")


def test_paye_at_first_boundary():
    result = calculate_paye(300000, TAX_BANDS)
    assert result == Decimal("21000.00")


def test_paye_within_second_band():
    result = calculate_paye(450000, TAX_BANDS)
    expected = Decimal("300000") * Decimal("0.07") + Decimal("150000") * Decimal("0.11")
    assert result == expected.quantize(Decimal("0.01"))


def test_paye_at_second_boundary():
    result = calculate_paye(600000, TAX_BANDS)
    expected = Decimal("300000") * Decimal("0.07") + Decimal("300000") * Decimal("0.11")
    assert result == expected.quantize(Decimal("0.01"))


def test_paye_deterministic():
    r1 = calculate_paye(800000, TAX_BANDS)
    r2 = calculate_paye(800000, TAX_BANDS)
    assert r1 == r2 == Decimal("84000.00")


# --- Nigeria Tax Act 2025 band boundary tests ---

def test_nta2025_within_free_band():
    # ₦500,000 falls entirely in the 0% band
    assert calculate_paye(500_000, NTA_2025_BANDS) == Decimal("0.00")


def test_nta2025_at_800k_boundary():
    # ₦800,000 is the top of the 0% band — still ₦0
    assert calculate_paye(800_000, NTA_2025_BANDS) == Decimal("0.00")


def test_nta2025_at_3m_boundary():
    # ₦3,000,000: (3M − 800K) × 15% = ₦330,000
    assert calculate_paye(3_000_000, NTA_2025_BANDS) == Decimal("330000.00")


def test_nta2025_at_12m_boundary():
    # ₦12,000,000: 330,000 + (9M × 18%) = ₦1,950,000
    assert calculate_paye(12_000_000, NTA_2025_BANDS) == Decimal("1950000.00")


def test_nta2025_at_25m_boundary():
    # ₦25,000,000: 1,950,000 + (13M × 21%) = ₦4,680,000
    assert calculate_paye(25_000_000, NTA_2025_BANDS) == Decimal("4680000.00")


def test_nta2025_at_50m_boundary():
    # ₦50,000,000: 4,680,000 + (25M × 23%) = ₦10,430,000
    assert calculate_paye(50_000_000, NTA_2025_BANDS) == Decimal("10430000.00")
