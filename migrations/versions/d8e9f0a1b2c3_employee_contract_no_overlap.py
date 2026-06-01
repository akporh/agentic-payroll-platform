"""MIG-18-B: btree_gist extension + no-overlap exclusion constraint on employee_contract

Revision ID: d8e9f0a1b2c3
Revises: f0a1b2c3d4e5
Create Date: 2026-05-31 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op

revision: str = "d8e9f0a1b2c3"
down_revision: Union[str, Sequence[str], None] = "f0a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")

    op.execute("""
        DO $$ BEGIN
            ALTER TABLE employee_contract
                ADD CONSTRAINT excl_employee_contract_no_overlap
                EXCLUDE USING gist (
                    employee_id WITH =,
                    daterange(start_date, COALESCE(end_date, 'infinity'::date), '[)') WITH &&
                );
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE employee_contract
            DROP CONSTRAINT IF EXISTS excl_employee_contract_no_overlap;
    """)
