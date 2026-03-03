"""enforce payroll_run state machine

Revision ID: 9901bc4ed0c5
Revises: f1107690f184
Create Date: 2026-02-26 03:51:02.573759

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9901bc4ed0c5'
down_revision: Union[str, Sequence[str], None] = 'f1107690f184'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
    CREATE OR REPLACE FUNCTION enforce_payroll_run_state_machine()
    RETURNS trigger AS $$
    BEGIN
        -- Immutable once PAID
        IF OLD.status = 'PAID' THEN
            RAISE EXCEPTION 'Cannot modify a PAID payroll run';
        END IF;

        -- Allowed transitions
        IF OLD.status = 'DRAFT' AND NEW.status NOT IN ('PROCESSING', 'CANCELLED') THEN
            RAISE EXCEPTION 'Invalid status transition from DRAFT to %', NEW.status;
        END IF;

        IF OLD.status = 'PROCESSING' AND NEW.status NOT IN ('COMPLETED', 'FAILED') THEN
            RAISE EXCEPTION 'Invalid status transition from PROCESSING to %', NEW.status;
        END IF;

        IF OLD.status = 'COMPLETED' AND NEW.status <> 'PAID' THEN
            RAISE EXCEPTION 'Invalid status transition from COMPLETED to %', NEW.status;
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS trg_payroll_run_state_machine ON payroll_run;
    """)

    op.execute("""
    CREATE TRIGGER trg_payroll_run_state_machine
    BEFORE UPDATE OF status ON payroll_run
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION enforce_payroll_run_state_machine();
    """)


def downgrade():
    op.execute("""
    DROP TRIGGER IF EXISTS trg_payroll_run_state_machine ON payroll_run;
    """)

    op.execute("""
    DROP FUNCTION IF EXISTS enforce_payroll_run_state_machine();
    """)
