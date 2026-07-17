"""Seed development_levy into statutory_rule.rules_jsonb + rename override key to annual_amount.

Statutory basis: Taxes and Levies (Approved List for Collection) Act, Cap T2
LFN 2004 (as amended) — State Governments are empowered to collect a
"Development Levy" of not more than ₦100 per annum per taxable individual
(Lagos State Internal Revenue Service confirms ₦100/year is the rate
actually charged). This is a distinct levy from the Nigeria Tax Act 2025's
corporate-level 4% Development Levy on companies' assessable profits — do
not conflate the two when reading this migration or the component's
metadata_json.

DEC-08 (docs/sprints/dev-levy-rule-pct/decisions.md): the workspace override
key is renamed monthly_amount -> annual_amount to match the levy's true
annual cadence (DEC-04). Both NG statutory_rule rows get an identical
development_levy key: {"amount": 100, "cadence": "ANNUAL"}. "ANNUAL" means
"apply via the engine's OR-gated January / first-paid-month triggers"
(sequential_executor._handle_development_levy_flat); "MONTHLY" remains a
valid override value for any workspace that deliberately wants flat-per-run
behaviour instead.

version is deliberately NOT bumped — it participates in an ORDER BY at
payroll.py's statutory-rule resolution query and bumping it is unrelated to
this data change.

Revision ID: 75c53c1c6a5b
Revises: d5b9cabb9d0e
Create Date: 2026-07-16
"""
from alembic import op

revision = "75c53c1c6a5b"
down_revision = "d5b9cabb9d0e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existence pre-check baked into the WHERE clause: skip rows that already
    # carry a development_levy key (idempotent re-run safety).
    op.execute("""
        UPDATE statutory_rule
        SET rules_jsonb = jsonb_set(
            rules_jsonb,
            '{development_levy}',
            '{"amount": 100, "cadence": "ANNUAL"}',
            true
        )
        WHERE country_code = 'NG'
          AND NOT (rules_jsonb ? 'development_levy')
    """)

    # Rename the stale workspace_override_key + refresh the now-inaccurate
    # "Flat monthly state levy" note on the platform component definition.
    op.execute("""
        UPDATE component_metadata
        SET metadata_json = jsonb_set(
            jsonb_set(
                metadata_json,
                '{engine_behavior,workspace_override_key}',
                '"annual_amount"',
                true
            ),
            '{legal_role,note}',
            '"Flat annual state levy (Development Levy — Taxes and Levies (Approved List for Collection) Act, Cap T2 LFN 2004): charged once per calendar year, in January and/or an employees first paid month. Configure the amount override per workspace via client_component_metadata."'::jsonb,
            true
        )
        WHERE component_code = 'DEVELOPMENT_LEVY'
          AND country_code   = 'NG'
          AND metadata_json -> 'engine_behavior' ->> 'workspace_override_key' = 'monthly_amount'
    """)


def downgrade() -> None:
    op.execute("""
        UPDATE statutory_rule
        SET rules_jsonb = rules_jsonb - 'development_levy'
        WHERE country_code = 'NG'
    """)

    op.execute("""
        UPDATE component_metadata
        SET metadata_json = jsonb_set(
            jsonb_set(
                metadata_json,
                '{engine_behavior,workspace_override_key}',
                '"monthly_amount"',
                true
            ),
            '{legal_role,note}',
            '"Flat monthly state levy — configure per workspace via client_component_metadata"'::jsonb,
            true
        )
        WHERE component_code = 'DEVELOPMENT_LEVY'
          AND country_code   = 'NG'
          AND metadata_json -> 'engine_behavior' ->> 'workspace_override_key' = 'annual_amount'
    """)
