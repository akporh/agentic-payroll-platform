"""Make snapshot physically Immutable

Revision ID: fe0bad282b7d
Revises: f45614d5aa92
Create Date: 2026-02-26 04:34:15.269914

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe0bad282b7d'
down_revision: Union[str, Sequence[str], None] = 'f45614d5aa92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
    CREATE OR REPLACE FUNCTION prevent_snapshot_update()
    RETURNS trigger AS $$
    BEGIN
        IF NEW.calculations_snapshot_json IS DISTINCT FROM OLD.calculations_snapshot_json THEN
            RAISE EXCEPTION 'calculations_snapshot_json is immutable';
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS trg_snapshot_immutable ON payroll_result;
    """)

    op.execute("""
    CREATE TRIGGER trg_snapshot_immutable
    BEFORE UPDATE OF calculations_snapshot_json ON payroll_result
    FOR EACH ROW
    WHEN (OLD.calculations_snapshot_json IS DISTINCT FROM NEW.calculations_snapshot_json)
    EXECUTE FUNCTION prevent_snapshot_update();
    """)

def downgrade() -> None:
    """Downgrade schema."""
    pass
