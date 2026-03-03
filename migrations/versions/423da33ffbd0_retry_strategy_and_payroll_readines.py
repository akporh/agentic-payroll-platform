"""Retry strategy and payroll readines

Revision ID: 423da33ffbd0
Revises: fe0bad282b7d
Create Date: 2026-02-26 07:35:17.352913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '423da33ffbd0'
down_revision: Union[str, Sequence[str], None] = 'fe0bad282b7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # ------------------------------------------------------------------
    # 1️⃣ Add retry_strategy column to workspace
    # ------------------------------------------------------------------

    op.add_column(
        "workspace",
        sa.Column(
            "retry_strategy",
            sa.String(length=30),
            nullable=True,
        ),
    )

    # Optional: add constraint for allowed values
    op.create_check_constraint(
        "ck_workspace_retry_strategy",
        "workspace",
        "retry_strategy IN ('FULL_RUN', 'PER_EMPLOYEE')"
    )

    # ------------------------------------------------------------------
    # 2️⃣ Create Payroll Readiness Validator Function
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
        v_count integer;
    BEGIN

        ------------------------------------------------------------
        -- LAYER 1: CONFIGURATION CHECKS
        ------------------------------------------------------------

        -- Salary definition exists and effective
        SELECT COUNT(*) INTO v_count
        FROM salary_definition sd
        WHERE sd.workspace_id = p_workspace_id
          AND (sd.effective_from IS NULL OR sd.effective_from <= p_period_end)
          AND (sd.effective_to IS NULL OR sd.effective_to >= p_period_start);

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code', 'NO_ACTIVE_SALARY_DEFINITION',
                'message', 'No active salary definition found for payroll period.'
            );
        END IF;


        -- Payroll rule exists
        SELECT COUNT(*) INTO v_count
        FROM payroll_rule pr
        WHERE pr.workspace_id = p_workspace_id
          AND pr.is_active = true;

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code', 'NO_ACTIVE_PAYROLL_RULE',
                'message', 'No active payroll rule configured.'
            );
        END IF;


        -- Retry strategy configured
        SELECT COUNT(*) INTO v_count
        FROM workspace w
        WHERE w.workspace_id = p_workspace_id
          AND w.retry_strategy IS NOT NULL;

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code', 'NO_RETRY_STRATEGY',
                'message', 'Retry strategy not configured for workspace.'
            );
        END IF;


        ------------------------------------------------------------
        -- LAYER 2: EMPLOYEE CHECKS
        ------------------------------------------------------------

        -- Active employees exist
        SELECT COUNT(*) INTO v_count
        FROM employee e
        WHERE e.workspace_id = p_workspace_id
          AND e.status = 'ACTIVE';

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code', 'NO_ACTIVE_EMPLOYEES',
                'message', 'No active employees found in workspace.'
            );
        END IF;


        -- Employees without active contract
        SELECT COUNT(*) INTO v_count
        FROM employee e
        LEFT JOIN employee_contract ec
            ON ec.employee_id = e.employee_id
            AND ec.end_date IS NULL
        WHERE e.workspace_id = p_workspace_id
          AND e.status = 'ACTIVE'
          AND ec.contract_id IS NULL;

        IF v_count > 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code', 'EMPLOYEE_WITHOUT_ACTIVE_CONTRACT',
                'message', v_count || ' active employees have no active contract.'
            );
        END IF;


        -- Contract not effective during period
        SELECT COUNT(*) INTO v_count
        FROM employee e
        JOIN employee_contract ec
            ON ec.employee_id = e.employee_id
        WHERE e.workspace_id = p_workspace_id
          AND e.status = 'ACTIVE'
          AND ec.start_date > p_period_end;

        IF v_count > 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code', 'CONTRACT_NOT_EFFECTIVE',
                'message', v_count || ' contracts not effective during payroll period.'
            );
        END IF;


        -- Salary definition referenced by contract not effective
        SELECT COUNT(*) INTO v_count
        FROM employee e
        JOIN employee_contract ec
            ON ec.employee_id = e.employee_id
        JOIN salary_definition sd
            ON sd.salary_definition_id = ec.salary_definition_id
        WHERE e.workspace_id = p_workspace_id
          AND e.status = 'ACTIVE'
          AND (
                sd.effective_from > p_period_end
                OR (sd.effective_to IS NOT NULL AND sd.effective_to < p_period_start)
              );

        IF v_count > 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code', 'SALARY_DEFINITION_NOT_EFFECTIVE',
                'message', v_count || ' contracts reference salary definitions not effective for period.'
            );
        END IF;


        ------------------------------------------------------------
        -- LAYER 3: EXECUTION GUARD
        ------------------------------------------------------------

        -- Payroll already exists
        SELECT COUNT(*) INTO v_count
        FROM payroll_run pr
        WHERE pr.workspace_id = p_workspace_id
          AND pr.period_start = p_period_start
          AND pr.period_end = p_period_end;

        IF v_count > 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code', 'PAYROLL_ALREADY_EXISTS',
                'message', 'Payroll already exists for this period.'
            );
        END IF;


        ------------------------------------------------------------
        -- RETURN RESULT
        ------------------------------------------------------------

        IF jsonb_array_length(v_errors) = 0 THEN
            RETURN jsonb_build_object(
                'ready', true,
                'errors', '[]'::jsonb
            );
        ELSE
            RETURN jsonb_build_object(
                'ready', false,
                'errors', v_errors
            );
        END IF;

    END;
    $$ LANGUAGE plpgsql;
    """)


def downgrade():
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS validate_payroll_readiness(uuid, date, date);")

    # Drop constraint
    op.drop_constraint("ck_workspace_retry_strategy", "workspace", type_="check")

    # Drop column
    op.drop_column("workspace", "retry_strategy")
