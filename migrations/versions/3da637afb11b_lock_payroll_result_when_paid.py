"""lock payroll_result when paid

Revision ID: 3da637afb11b
Revises: d9828ee962a2
Create Date: 2026-02-26 04:25:35.492863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3da637afb11b'
down_revision: Union[str, Sequence[str], None] = 'd9828ee962a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
    CREATE OR REPLACE FUNCTION prevent_result_modification_if_paid()
    RETURNS trigger AS $$
    DECLARE
        parent_status TEXT;
    BEGIN
        SELECT status INTO parent_status
        FROM payroll_run
        WHERE payroll_run_id = COALESCE(NEW.payroll_run_id, OLD.payroll_run_id);

        IF parent_status = 'PAID' THEN
            RAISE EXCEPTION
            'Cannot modify payroll_result because parent payroll_run is PAID';
        END IF;

        RETURN COALESCE(NEW, OLD);
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS trg_prevent_paid_result_update ON payroll_result;
    """)

    op.execute("""
    CREATE TRIGGER trg_prevent_paid_result_update
    BEFORE UPDATE ON payroll_result
    FOR EACH ROW
    EXECUTE FUNCTION prevent_result_modification_if_paid();
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS trg_prevent_paid_result_delete ON payroll_result;
    """)

    op.execute("""
    CREATE TRIGGER trg_prevent_paid_result_delete
    BEFORE DELETE ON payroll_result
    FOR EACH ROW
    EXECUTE FUNCTION prevent_result_modification_if_paid();
    """)

def downgrade() -> None:
    """Downgrade schema."""
    pass
