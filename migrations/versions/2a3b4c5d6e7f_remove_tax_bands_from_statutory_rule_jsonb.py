"""remove tax_bands from statutory_rule.rules_jsonb

Tax bands are the authoritative source of truth in the tax_band table
(FK'd to statutory_rule). Having them duplicated in rules_jsonb creates
a split source of truth — any rate change would need updating in two
places. The engine already reads from the tax_band table exclusively.

This migration:
1. Strips the `tax_bands` key from all existing rules_jsonb rows.
2. Adds a CHECK constraint so it can never be re-inserted.

Revision ID: 2a3b4c5d6e7f
Revises: 1f644216db63
Create Date: 2026-03-19
"""
from alembic import op

revision = '2a3b4c5d6e7f'
down_revision = '1f644216db63'
branch_labels = None
depends_on = None


def upgrade():
    # Strip tax_bands from all existing statutory_rule rows
    op.execute("""
        UPDATE statutory_rule
        SET rules_jsonb = rules_jsonb - 'tax_bands'
        WHERE rules_jsonb ? 'tax_bands'
    """)

    # Prevent tax_bands from being inserted into rules_jsonb in future
    op.execute("""
        ALTER TABLE statutory_rule
        ADD CONSTRAINT chk_statutory_rule_no_tax_bands_in_jsonb
        CHECK (NOT (rules_jsonb ? 'tax_bands'))
    """)


def downgrade():
    op.execute("""
        ALTER TABLE statutory_rule
        DROP CONSTRAINT IF EXISTS chk_statutory_rule_no_tax_bands_in_jsonb
    """)

    # Restore tax_bands from the tax_band table back into rules_jsonb
    op.execute("""
        UPDATE statutory_rule sr
        SET rules_jsonb = rules_jsonb || jsonb_build_object(
            'tax_bands',
            COALESCE(
                (
                    SELECT jsonb_agg(
                        jsonb_build_object(
                            'lower_limit', tb.lower_limit,
                            'upper_limit', tb.upper_limit,
                            'rate',        tb.rate
                        )
                        ORDER BY tb.lower_limit
                    )
                    FROM tax_band tb
                    WHERE tb.statutory_rule_id = sr.statutory_rule_id
                ),
                '[]'::jsonb
            )
        )
    """)
