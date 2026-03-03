"""lock salary_definition when paid

Revision ID: f45614d5aa92
Revises: 3da637afb11b
Create Date: 2026-02-26 04:29:24.152326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f45614d5aa92'
down_revision: Union[str, Sequence[str], None] = '3da637afb11b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.execute("""
    CREATE OR REPLACE FUNCTION prevent_salary_definition_change_if_used()
    RETURNS trigger AS $$
    DECLARE
        used_count INTEGER;
    BEGIN
        SELECT COUNT(*) INTO used_count
        FROM employee_contract ec
        JOIN payroll_result pr ON pr.employee_id = ec.employee_id
        JOIN payroll_run run ON run.payroll_run_id = pr.payroll_run_id
        WHERE ec.salary_definition_id = OLD.salary_definition_id
          AND run.status = 'PAID';

        IF used_count > 0 THEN
            RAISE EXCEPTION 
            'Cannot modify salary_definition % because it was used in a PAID payroll',
            OLD.salary_definition_id;
        END IF;

        RETURN COALESCE(NEW, OLD);
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS trg_prevent_salary_definition_update ON salary_definition;
    """)

    op.execute("""
    CREATE TRIGGER trg_prevent_salary_definition_update
    BEFORE UPDATE ON salary_definition
    FOR EACH ROW
    EXECUTE FUNCTION prevent_salary_definition_change_if_used();
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS trg_prevent_salary_definition_delete ON salary_definition;
    """)

    op.execute("""
    CREATE TRIGGER trg_prevent_salary_definition_delete
    BEFORE DELETE ON salary_definition
    FOR EACH ROW
    EXECUTE FUNCTION prevent_salary_definition_change_if_used();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
