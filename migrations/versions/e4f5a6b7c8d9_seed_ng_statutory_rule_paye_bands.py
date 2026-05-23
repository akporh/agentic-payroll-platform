"""Seed Nigerian statutory rule, PAYE tax bands, and fix RENT_RELIEF effective_from.

Creates the NG statutory_rule row (CUMULATIVE PAYE, pension 8%/10%,
rent relief 20% rate / ₦500,000 cap) and the six PITA tax bands.
Also corrects RENT_RELIEF component_metadata.effective_from from
2025-01-01 to 2026-01-01 (Nigeria Tax Act 2025 came into force 1 Jan 2026).

All INSERTs are idempotent (ON CONFLICT DO NOTHING).

Revision ID: e4f5a6b7c8d9
Revises: f0a1b2c3d4e5
Create Date: 2026-05-23
"""
import sqlalchemy as sa
from alembic import op

revision: str = "e4f5a6b7c8d9"
down_revision: str = "f0a1b2c3d4e5"
branch_labels = None
depends_on = None

# Fixed UUID so the migration is idempotent across re-runs / environments.
_SR_ID = "a0000000-0000-0000-0000-000000000001"

_RULES_JSONB = """{
  "pension": {
    "employee_rate": "0.08",
    "employer_rate": "0.10"
  },
  "reliefs": {
    "rent_relief": {
      "rate": "0.20",
      "cap":  "500000"
    }
  }
}"""

# Nigerian PITA tax bands (₦ annual brackets, rates per FIRS schedule).
_TAX_BANDS = [
    (0,         300_000,   "0.07"),
    (300_000,   600_000,   "0.11"),
    (600_000,   1_100_000, "0.15"),
    (1_100_000, 1_600_000, "0.19"),
    (1_600_000, 3_200_000, "0.21"),
    (3_200_000, None,      "0.24"),
]


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Seed statutory_rule ------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO statutory_rule
            (statutory_rule_id, state, version, rules_jsonb,
             tax_method, country_code, effective_from)
        VALUES
            (:id, 'NATIONAL', 1, CAST(:rules AS jsonb),
             'CUMULATIVE', 'NG', '2026-01-01')
        ON CONFLICT (country_code, effective_from) DO NOTHING
    """), {"id": _SR_ID, "rules": _RULES_JSONB})

    # Resolve the actual ID in case a row already existed before this migration.
    row = conn.execute(sa.text("""
        SELECT statutory_rule_id::text
        FROM statutory_rule
        WHERE country_code = 'NG'
          AND effective_from = '2026-01-01'
    """)).fetchone()
    sr_id = row[0] if row else _SR_ID

    # 2. Seed tax bands (skip each band if already present for this rule) ----
    for lower, upper, rate in _TAX_BANDS:
        conn.execute(sa.text("""
            INSERT INTO tax_band
                (tax_band_id, statutory_rule_id, lower_limit, upper_limit, rate)
            SELECT
                gen_random_uuid(), CAST(:sr_id AS uuid), :lower, :upper, :rate
            WHERE NOT EXISTS (
                SELECT 1 FROM tax_band
                WHERE statutory_rule_id = CAST(:sr_id AS uuid)
                  AND lower_limit = :lower
            )
        """), {"sr_id": sr_id, "lower": lower, "upper": upper, "rate": rate})

    # 3. Fix RENT_RELIEF effective_from: 2025-01-01 → 2026-01-01 ------------
    conn.execute(sa.text("""
        UPDATE component_metadata
           SET effective_from = '2026-01-01'
         WHERE component_code = 'RENT_RELIEF'
           AND country_code   = 'NG'
           AND effective_from = '2025-01-01'
    """))


def downgrade() -> None:
    conn = op.get_bind()

    # Remove tax bands seeded by this migration.
    conn.execute(sa.text("""
        DELETE FROM tax_band
        WHERE statutory_rule_id = CAST(:id AS uuid)
    """), {"id": _SR_ID})

    # Remove the statutory_rule row only if it was inserted by this migration.
    conn.execute(sa.text("""
        DELETE FROM statutory_rule
        WHERE statutory_rule_id = CAST(:id AS uuid)
    """), {"id": _SR_ID})

    # Revert RENT_RELIEF effective_from.
    conn.execute(sa.text("""
        UPDATE component_metadata
           SET effective_from = '2025-01-01'
         WHERE component_code = 'RENT_RELIEF'
           AND country_code   = 'NG'
           AND effective_from = '2026-01-01'
    """))
