"""move_retry_strategy_to_payroll_run

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-03-11 00:00:00.000000

Design fix: retry_strategy belongs to payroll_run, not workspace.

Changes
-------
1. Add payroll_run.retry_strategy (VARCHAR, NOT NULL, default PER_EMPLOYEE).
2. Backfill existing runs.
3. Replace validate_payroll_readiness() — remove the NO_RETRY_STRATEGY check
   so workspaces without a retry_strategy can still run payroll.
4. Drop workspace.retry_strategy check constraint and column.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, Sequence[str], None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # ------------------------------------------------------------------
    # 1. Add retry_strategy to payroll_run — default fills existing rows
    #    at the DDL level, bypassing row-level UPDATE triggers (including
    #    prevent_paid_payroll_run_update).
    # ------------------------------------------------------------------
    op.add_column(
        'payroll_run',
        sa.Column(
            'retry_strategy',
            sa.String(20),
            nullable=False,
            server_default='PER_EMPLOYEE',
        ),
    )

    op.create_check_constraint(
        'ck_payroll_run_retry_strategy',
        'payroll_run',
        "retry_strategy IN ('PER_EMPLOYEE', 'FULL_RUN')",
    )

    # ------------------------------------------------------------------
    # 3. Replace validate_payroll_readiness — remove NO_RETRY_STRATEGY
    # ------------------------------------------------------------------
    op.execute("""
    CREATE OR REPLACE FUNCTION validate_payroll_readiness(
        p_workspace_id uuid,
        p_period_start date,
        p_period_end date
    )
    RETURNS jsonb AS $$
    DECLARE
        v_errors jsonb := '[]'::jsonb;
        v_count  integer;
        v_country character varying;
    BEGIN

        ----------------------------------------------------------------
        -- LAYER 0: WORKSPACE STATE
        ----------------------------------------------------------------
        SELECT COUNT(*) INTO v_count
        FROM workspace
        WHERE workspace_id = p_workspace_id
          AND status = 'LIVE';

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code',    'WORKSPACE_NOT_LIVE',
                'message', 'Workspace must be LIVE before running payroll.'
            );
        END IF;

        ----------------------------------------------------------------
        -- LAYER 1: STATUTORY CONFIGURATION
        ----------------------------------------------------------------
        SELECT COUNT(*) INTO v_count FROM statutory_rule;

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code',    'NO_STATUTORY_RULE',
                'message', 'No statutory rule configured.'
            );
        END IF;

        SELECT COUNT(*) INTO v_count FROM tax_band;

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code',    'NO_TAX_BANDS',
                'message', 'No tax bands configured.'
            );
        END IF;

        ----------------------------------------------------------------
        -- LAYER 2: COMPONENT METADATA
        ----------------------------------------------------------------
        SELECT country_code INTO v_country
        FROM workspace
        WHERE workspace_id = p_workspace_id;

        SELECT COUNT(*) INTO v_count
        FROM component_metadata
        WHERE country_code = v_country
          AND is_active = true;

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code',    'NO_ACTIVE_COMPONENT_METADATA',
                'message', 'No active component metadata configured.'
            );
        END IF;

        ----------------------------------------------------------------
        -- RETURN
        ----------------------------------------------------------------
        IF jsonb_array_length(v_errors) = 0 THEN
            RETURN jsonb_build_object('ready', true,  'errors', '[]'::jsonb);
        ELSE
            RETURN jsonb_build_object('ready', false, 'errors', v_errors);
        END IF;

    END;
    $$ LANGUAGE plpgsql;
    """)

    # ------------------------------------------------------------------
    # 4. Remove workspace.retry_strategy — it no longer belongs here
    # ------------------------------------------------------------------
    # Drop constraint first (may or may not exist depending on migration history)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'ck_workspace_retry_strategy'
            ) THEN
                ALTER TABLE workspace DROP CONSTRAINT ck_workspace_retry_strategy;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'workspace' AND column_name = 'retry_strategy'
            ) THEN
                ALTER TABLE workspace DROP COLUMN retry_strategy;
            END IF;
        END $$;
    """)


def downgrade():
    # Restore workspace.retry_strategy
    op.add_column(
        'workspace',
        sa.Column('retry_strategy', sa.String(30), nullable=True),
    )
    op.create_check_constraint(
        'ck_workspace_retry_strategy',
        'workspace',
        "retry_strategy IN ('FULL_RUN', 'PER_EMPLOYEE')",
    )

    # Remove payroll_run.retry_strategy
    op.drop_constraint('ck_payroll_run_retry_strategy', 'payroll_run', type_='check')
    op.drop_column('payroll_run', 'retry_strategy')
