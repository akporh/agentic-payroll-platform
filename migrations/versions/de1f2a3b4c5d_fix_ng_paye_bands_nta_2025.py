"""Fix NG PAYE tax bands to Nigeria Tax Act 2025 schedule.

The seed migration e4f5a6b7c8d9 set effective_from=2026-01-01 and referenced
the Nigeria Tax Act 2025, but seeded the old PITA bands (7/11/15/19/21/24%).
The correct NTA 2025 schedule is: 0% / 15% / 18% / 21% / 23% / 25% with
different bracket thresholds, including a ₦800,000 tax-free band.

This migration replaces the six old bands with the six correct ones.

Revision ID: de1f2a3b4c5d
Revises: cd2ef3a4b5c6
Create Date: 2026-06-20
"""
import sqlalchemy as sa
from alembic import op

revision: str = "de1f2a3b4c5d"
down_revision: str = "cd2ef3a4b5c6"
branch_labels = None
depends_on = None

_OLD_BANDS = [
    (0,         300_000,   "0.07"),
    (300_000,   600_000,   "0.11"),
    (600_000,   1_100_000, "0.15"),
    (1_100_000, 1_600_000, "0.19"),
    (1_600_000, 3_200_000, "0.21"),
    (3_200_000, None,      "0.24"),
]

_NEW_BANDS = [
    (0,          800_000,    "0.00"),
    (800_000,    3_000_000,  "0.15"),
    (3_000_000,  12_000_000, "0.18"),
    (12_000_000, 25_000_000, "0.21"),
    (25_000_000, 50_000_000, "0.23"),
    (50_000_000, None,       "0.25"),
]


def _resolve_sr_id(conn) -> str | None:
    row = conn.execute(sa.text("""
        SELECT statutory_rule_id::text
        FROM statutory_rule
        WHERE country_code   = 'NG'
          AND effective_from = '2026-01-01'
    """)).fetchone()
    return row[0] if row else None


def _replace_bands(conn, sr_id: str, bands: list[tuple]) -> None:
    conn.execute(sa.text(
        "DELETE FROM tax_band WHERE statutory_rule_id = CAST(:sr_id AS uuid)"
    ), {"sr_id": sr_id})

    for lower, upper, rate in bands:
        conn.execute(sa.text("""
            INSERT INTO tax_band
                (tax_band_id, statutory_rule_id, lower_limit, upper_limit, rate)
            VALUES (
                gen_random_uuid(),
                CAST(:sr_id AS uuid),
                :lower,
                :upper,
                :rate
            )
        """), {"sr_id": sr_id, "lower": lower, "upper": upper, "rate": rate})


def upgrade() -> None:
    conn = op.get_bind()
    sr_id = _resolve_sr_id(conn)
    if sr_id is None:
        return
    _replace_bands(conn, sr_id, _NEW_BANDS)


def downgrade() -> None:
    conn = op.get_bind()
    sr_id = _resolve_sr_id(conn)
    if sr_id is None:
        return
    _replace_bands(conn, sr_id, _OLD_BANDS)
