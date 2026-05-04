"""Add CHECK constraint on payroll_rule.rule_definition_json calculation_method — Sprint 13 M3 D3

Enumerates all 5 valid calculation_method values. Pre-checks that no existing rows
have an unrecognised value before creating the constraint, so the migration is
safe to run on a live database.

Revision ID: 2b3c4d5e6f7a
Revises: 1a2b3c4d5e6f
Create Date: 2026-05-04 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = "2b3c4d5e6f7a"
down_revision: Union[str, Sequence[str], None] = "1a2b3c4d5e6f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_VALID_METHODS = (
    "unit_multiplier",
    "daily_rate_deduction",
    "fixed_amount",
    "ot_multiplier",
    "percentage_of_sum",
)


def upgrade() -> None:
    valid_list = ", ".join(f"'{m}'" for m in _VALID_METHODS)
    op.execute(f"""
    DO $$
    DECLARE bad_count INT;
    BEGIN
        SELECT COUNT(*) INTO bad_count
        FROM payroll_rule
        WHERE rule_definition_json->>'calculation_method' IS NOT NULL
          AND rule_definition_json->>'calculation_method' NOT IN ({valid_list});

        IF bad_count > 0 THEN
            RAISE EXCEPTION
                'payroll_rule has % rows with unrecognised calculation_method — '
                'resolve before applying migration 2b3c4d5e6f7a',
                bad_count;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints
            WHERE table_name       = 'payroll_rule'
              AND constraint_name  = 'chk_payroll_rule_calculation_method'
              AND constraint_type  = 'CHECK'
        ) THEN
            ALTER TABLE payroll_rule
            ADD CONSTRAINT chk_payroll_rule_calculation_method
            CHECK (
                rule_definition_json->>'calculation_method' IS NULL
                OR rule_definition_json->>'calculation_method' IN ({valid_list})
            );
        END IF;
    END $$;
    """)


def downgrade() -> None:
    op.execute("""
    ALTER TABLE payroll_rule
    DROP CONSTRAINT IF EXISTS chk_payroll_rule_calculation_method;
    """)
