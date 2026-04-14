"""Add non-negative CHECK constraint on payroll_input.quantity (INP10)

Revision ID: f8a9b0c1d2e3
Revises: a8b9c0d1e2f3
Create Date: 2026-04-13

"""
from typing import Sequence, Union

from alembic import op


revision: str = "f8a9b0c1d2e3"
down_revision: Union[str, Sequence[str], None] = "a8b9c0d1e2f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Pre-check: fail fast if negative quantities already exist.
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM payroll_input WHERE quantity < 0) THEN
                RAISE EXCEPTION
                    'Cannot add non-negative constraint: negative quantities exist in payroll_input';
            END IF;
        END $$;
    """)

    # Add constraint only if it does not already exist.
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'ck_payroll_input_quantity_non_negative'
            ) THEN
                ALTER TABLE payroll_input
                    ADD CONSTRAINT ck_payroll_input_quantity_non_negative
                    CHECK (quantity >= 0);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'ck_payroll_input_quantity_non_negative'
            ) THEN
                ALTER TABLE payroll_input
                    DROP CONSTRAINT ck_payroll_input_quantity_non_negative;
            END IF;
        END $$;
    """)
