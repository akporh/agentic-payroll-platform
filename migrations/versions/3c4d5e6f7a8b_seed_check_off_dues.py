"""Seed CHECK_OFF_DUES component_metadata + workspace payroll_rule — Sprint 13 M3

Part A: Seeds the platform component_metadata row for CHECK_OFF_DUES.
  - component_class = 'statutory_deduction'
  - calculation_method = 'salary_component'  (D1: Path (b) — executor reads
    the value injected by the rule evaluator; Path (a) is prohibited)
  - execution_priority = 450  (after LIFE_INSURANCE=440, before NET_PAY=500)

Part B: Seeds the workspace-specific payroll_rule for Client B.
  - calculation_method = 'percentage_of_sum'
  - rate = 0.02 (2%), base = BASIC + HOUSING + TRANSPORT
  - eligibility_field = 'is_union_member' (C2: BASIC_MONTHLY → BASIC correction applied)
  - workspace resolved by name 'Client B'; migrates silently if workspace not found.

Revision ID: 3c4d5e6f7a8b
Revises: 2b3c4d5e6f7a
Create Date: 2026-05-04 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = "3c4d5e6f7a8b"
down_revision: Union[str, Sequence[str], None] = "2b3c4d5e6f7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Part A — platform component_metadata row
    op.execute("""
    INSERT INTO component_metadata (
        component_metadata_id,
        component_code,
        country_code,
        version,
        component_class,
        calculation_method,
        execution_priority,
        effective_from,
        is_active,
        metadata_json
    ) VALUES (
        gen_random_uuid(),
        'CHECK_OFF_DUES',
        'NG',
        1,
        'statutory_deduction',
        'salary_component',
        450,
        '2026-01-01',
        TRUE,
        '{}'::jsonb
    )
    ON CONFLICT (component_code, country_code, version) DO NOTHING;
    """)

    # Part B — workspace payroll_rule for Client B
    # Silently no-ops if workspace named 'Client B' does not exist.
    op.execute("""
    DO $$
    DECLARE _wid UUID;
    BEGIN
        SELECT workspace_id INTO _wid
        FROM workspace
        WHERE name = 'Client B'
        LIMIT 1;

        IF _wid IS NOT NULL THEN
            INSERT INTO payroll_rule (
                rule_id,
                workspace_id,
                rule_name,
                rule_type,
                rule_definition_json,
                is_active
            ) VALUES (
                gen_random_uuid(),
                _wid,
                'Check-Off Dues',
                'DEDUCTION',
                '{
                    "calculation_method": "percentage_of_sum",
                    "rate": 0.02,
                    "base_components": ["BASIC", "HOUSING", "TRANSPORT"],
                    "eligibility_field": "is_union_member"
                }'::jsonb,
                TRUE
            )
            ON CONFLICT DO NOTHING;
        END IF;
    END $$;
    """)


def downgrade() -> None:
    # Remove the workspace payroll_rule seed for Client B
    op.execute("""
    DO $$
    DECLARE _wid UUID;
    BEGIN
        SELECT workspace_id INTO _wid
        FROM workspace
        WHERE name = 'Client B'
        LIMIT 1;

        IF _wid IS NOT NULL THEN
            DELETE FROM payroll_rule
            WHERE workspace_id = _wid
              AND rule_name = 'Check-Off Dues'
              AND rule_definition_json->>'calculation_method' = 'percentage_of_sum';
        END IF;
    END $$;
    """)

    # Remove platform component_metadata row
    op.execute("""
    DELETE FROM component_metadata
    WHERE component_code = 'CHECK_OFF_DUES'
      AND country_code   = 'NG'
      AND version        = 1;
    """)
