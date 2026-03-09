"""enforce_workspace_live_before_payroll

Revision ID: 0daab4ac893b
Revises: 4907cf6eb08f
Create Date: 2026-03-03 07:07:43.485272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0daab4ac893b'
down_revision: Union[str, Sequence[str], None] = '4907cf6eb08f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.execute("""
        CREATE OR REPLACE FUNCTION enforce_workspace_live_before_payroll()
        RETURNS trigger AS $$
        DECLARE
            v_status workspace_status;
        BEGIN

            SELECT status INTO v_status
            FROM workspace
            WHERE workspace_id = NEW.workspace_id;

            IF v_status IS DISTINCT FROM 'LIVE' THEN
                RAISE EXCEPTION
                    'Cannot create payroll_run: workspace % is not LIVE (current status: %)',
                    NEW.workspace_id,
                    v_status;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)
    
    op.execute("""
        CREATE TRIGGER trg_enforce_workspace_live
        BEFORE INSERT ON payroll_run
        FOR EACH ROW
        EXECUTE FUNCTION enforce_workspace_live_before_payroll();
        """)

def downgrade():
    op.execute("DROP TRIGGER IF EXISTS trg_enforce_workspace_live ON payroll_run;")
    op.execute("DROP FUNCTION IF EXISTS enforce_workspace_live_before_payroll();")
