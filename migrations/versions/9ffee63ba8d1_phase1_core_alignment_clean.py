"""
Phase 1 Core Alignment Migration (Clean)

Includes:
- Payroll core alignment to latest ERD Phase 1
- Removes incorrect salary_definition.employee_id
- Adds payroll run period + totals
- Adds payroll result generated_at
- Fixes payroll_rule naming + metadata
- Adds event_store.workspace_id only

Excludes intentionally:
- account.owner_email
- grade_history
- event_store.actor_user_id
- Phase 2 tax authority tables
"""


from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ffee63ba8d1'
down_revision: Union[str, Sequence[str], None] = 'a2ae0981bef9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    # =========================================================
    # 1. WORKSPACE METADATA (ERD Core Tenant Info)
    # =========================================================
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='workspace'
            AND column_name='country_code'
        ) THEN
            ALTER TABLE workspace ADD COLUMN country_code VARCHAR(10);
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='workspace'
            AND column_name='base_currency'
        ) THEN
            ALTER TABLE workspace ADD COLUMN base_currency VARCHAR(10);
        END IF;
    END $$;
    """)

    # =========================================================
    # 2. SALARY_DEFINITION TEMPLATE FIX
    # Remove employee binding (templates only)
    # =========================================================
    op.execute("""
    ALTER TABLE salary_definition
    DROP COLUMN IF EXISTS employee_id;
    """)

    # =========================================================
    # 3. PAYROLL_RUN: Add calendar + totals
    # =========================================================
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='payroll_run'
            AND column_name='period_start'
        ) THEN
            ALTER TABLE payroll_run ADD COLUMN period_start DATE;
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='payroll_run'
            AND column_name='period_end'
        ) THEN
            ALTER TABLE payroll_run ADD COLUMN period_end DATE;
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='payroll_run'
            AND column_name='pay_date'
        ) THEN
            ALTER TABLE payroll_run ADD COLUMN pay_date DATE;
        END IF;
    END $$;
    """)

    op.execute("""
    ALTER TABLE payroll_run
    ADD COLUMN IF NOT EXISTS total_gross_pay NUMERIC;
    """)

    op.execute("""
    ALTER TABLE payroll_run
    ADD COLUMN IF NOT EXISTS total_deduction NUMERIC;
    """)

    op.execute("""
    ALTER TABLE payroll_run
    ADD COLUMN IF NOT EXISTS total_net_pay NUMERIC;
    """)

    # =========================================================
    # 4. PAYROLL_RESULT: Add generated_at
    # =========================================================
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='payroll_result'
            AND column_name='generated_at'
        ) THEN
            ALTER TABLE payroll_result
            ADD COLUMN generated_at TIMESTAMP DEFAULT now();
        END IF;
    END $$;
    """)

    # =========================================================
    # 5. PAYROLL_RULE: Rename columns to ERD standard
    # =========================================================
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='payroll_rule'
            AND column_name='payroll_rule_id'
        ) THEN
            ALTER TABLE payroll_rule
            RENAME COLUMN payroll_rule_id TO rule_id;
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='payroll_rule'
            AND column_name='name'
        ) THEN
            ALTER TABLE payroll_rule
            RENAME COLUMN name TO rule_name;
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='payroll_rule'
            AND column_name='rule_jsonb'
        ) THEN
            ALTER TABLE payroll_rule
            RENAME COLUMN rule_jsonb TO rule_definition_json;
        END IF;
    END $$;
    """)

    # Add missing metadata safely
    op.execute("""
    ALTER TABLE payroll_rule
    ADD COLUMN IF NOT EXISTS rule_type VARCHAR(100);
    """)

    op.execute("""
    ALTER TABLE payroll_rule
    ADD COLUMN IF NOT EXISTS schema_version INT DEFAULT 1;
    """)

    op.execute("""
    ALTER TABLE payroll_rule
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
    """)

    op.execute("""
    ALTER TABLE payroll_rule
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT now();
    """)

    # =========================================================
    # 6. EVENT_STORE: Add workspace_id only (no actor field)
    # =========================================================
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='event_store'
            AND column_name='workspace_id'
        ) THEN
            ALTER TABLE event_store ADD COLUMN workspace_id UUID;
        END IF;
    END $$;
    """)


def downgrade():
    # MVP downgrade not required
    pass

