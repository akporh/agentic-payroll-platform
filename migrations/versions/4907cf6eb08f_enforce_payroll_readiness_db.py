"""enforce_payroll_readiness_DB

Revision ID: 4907cf6eb08f
Revises: 585ee430c647
Create Date: 2026-03-03 06:44:15.192109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4907cf6eb08f'
down_revision: Union[str, Sequence[str], None] = '585ee430c647'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
    CREATE OR REPLACE FUNCTION enforce_payroll_readiness()
    RETURNS trigger AS $$
    DECLARE
        v_result jsonb;
        v_ready boolean;
    BEGIN

        v_result := validate_payroll_readiness(
            NEW.workspace_id,
            NEW.period_start,
            NEW.period_end
        );

        v_ready := (v_result->>'ready')::boolean;

        IF v_ready IS FALSE THEN
            RAISE EXCEPTION
            'Payroll readiness failed: %',
            v_result->>'errors';
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE TRIGGER trg_enforce_payroll_readiness
    BEFORE INSERT ON payroll_run
    FOR EACH ROW
    EXECUTE FUNCTION enforce_payroll_readiness();
    """)


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS trg_enforce_payroll_readiness ON payroll_run;")
    op.execute("DROP FUNCTION IF EXISTS enforce_payroll_readiness();")
