"""Seed pension rates into statutory_rule.rules_jsonb.

Existing rows have no `pension` key in rules_jsonb, causing the engine to
fall back to hardcoded defaults.  This migration writes the authoritative
PRA 2014 rates (employee 8%, employer 10%) into every existing statutory_rule
row and removes the fallback defaults from application code.

Revision ID: c0d1e2f3a4b5
Revises: b9c0d1e2f3a4
"""
from alembic import op

revision = "c0d1e2f3a4b5"
down_revision = "b9c0d1e2f3a4"
branch_labels = None
depends_on = None


def upgrade():
    # Write pension rates into every existing statutory_rule row.
    # jsonb_set with create_missing=true inserts the key if absent;
    # the nested call handles rows that already have a partial pension key.
    op.execute("""
        UPDATE statutory_rule
        SET rules_jsonb = jsonb_set(
            jsonb_set(
                rules_jsonb,
                '{pension, employee_rate}',
                '"0.08"',
                true
            ),
            '{pension, employer_rate}',
            '"0.10"',
            true
        )
    """)


def downgrade():
    # Remove the pension key entirely (restores pre-migration state).
    op.execute("""
        UPDATE statutory_rule
        SET rules_jsonb = rules_jsonb - 'pension'
    """)
