"""upgrade_validate_payroll_readiness_function

Revision ID: 585ee430c647
Revises: b2e7a07972b7
Create Date: 2026-03-03 06:18:48.712318

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '585ee430c647'
down_revision: Union[str, Sequence[str], None] = 'b2e7a07972b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
    CREATE OR REPLACE FUNCTION public.validate_payroll_readiness(
        p_workspace_id uuid,
        p_period_start date,
        p_period_end date
    )
    RETURNS jsonb AS $$
    DECLARE
        v_errors jsonb := '[]'::jsonb;
        v_count integer;
        v_country character varying;
    BEGIN

        ------------------------------------------------------------
        -- LAYER 0: WORKSPACE STATE
        ------------------------------------------------------------

        SELECT COUNT(*) INTO v_count
        FROM workspace
        WHERE workspace_id = p_workspace_id
          AND status = 'LIVE';

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code', 'WORKSPACE_NOT_LIVE',
                'message', 'Workspace must be LIVE before running payroll.'
            );
        END IF;


        ------------------------------------------------------------
        -- LAYER 1: STATUTORY CHECKS
        ------------------------------------------------------------

        SELECT country_code INTO v_country
        FROM workspace
        WHERE workspace_id = p_workspace_id;

        SELECT COUNT(*) INTO v_count FROM statutory_rule;

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code', 'NO_STATUTORY_RULE',
                'message', 'No statutory rule configured.'
            );
        END IF;

        SELECT COUNT(*) INTO v_count FROM tax_band;

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code', 'NO_TAX_BANDS',
                'message', 'No tax bands configured.'
            );
        END IF;


        ------------------------------------------------------------
        -- LAYER 2: COMPONENT METADATA
        ------------------------------------------------------------

        SELECT COUNT(*) INTO v_count
        FROM component_metadata
        WHERE country_code = v_country
          AND is_active = true;

        IF v_count = 0 THEN
            v_errors := v_errors || jsonb_build_object(
                'code', 'NO_ACTIVE_COMPONENT_METADATA',
                'message', 'No active component metadata configured.'
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
    op.execute("""
        DROP FUNCTION IF EXISTS public.validate_payroll_readiness(uuid, date, date);
    """)