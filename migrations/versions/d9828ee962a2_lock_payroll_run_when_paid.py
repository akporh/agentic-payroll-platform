"""lock payroll_run when paid

Revision ID: d9828ee962a2
Revises: 9901bc4ed0c5
Create Date: 2026-02-26 04:06:36.149252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9828ee962a2'
down_revision: Union[str, Sequence[str], None] = '9901bc4ed0c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
    CREATE OR REPLACE FUNCTION prevent_paid_payroll_run_update()
    RETURNS trigger AS $$
    BEGIN
        RAISE EXCEPTION 
            'Payroll run % is PAID and cannot be modified',
            OLD.payroll_run_id;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS trg_prevent_paid_run_update ON payroll_run;
    """)

    op.execute("""
    CREATE TRIGGER trg_prevent_paid_run_update
    BEFORE UPDATE ON payroll_run
    FOR EACH ROW
    WHEN (OLD.status = 'PAID')
    EXECUTE FUNCTION prevent_paid_payroll_run_update();
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS trg_prevent_paid_run_delete ON payroll_run;
    """)

    op.execute("""
    CREATE TRIGGER trg_prevent_paid_run_delete
    BEFORE DELETE ON payroll_run
    FOR EACH ROW
    WHEN (OLD.status = 'PAID')
    EXECUTE FUNCTION prevent_paid_payroll_run_update();
    """)


def downgrade():
    op.execute("""
    DROP TRIGGER IF EXISTS trg_prevent_paid_run_update ON payroll_run;
    """)

    op.execute("""
    DROP FUNCTION IF EXISTS prevent_paid_payroll_run_update();
    """)
