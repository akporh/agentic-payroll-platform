"""MIG-18-C: Retire FULL_RUN from retry_strategy CHECK constraint

Revision ID: f7a1b2c3d4e5
Revises: f0a1b2c3d4e5
Create Date: 2026-05-31 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op

revision: str = "f7a1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = "f0a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE payroll_run DROP CONSTRAINT ck_payroll_run_retry_strategy;
        EXCEPTION WHEN undefined_object THEN NULL; END $$;
    """)

    op.execute("""
        ALTER TABLE payroll_run
            ADD CONSTRAINT ck_payroll_run_retry_strategy
            CHECK (retry_strategy IN ('PER_EMPLOYEE'));
    """)


def downgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE payroll_run DROP CONSTRAINT ck_payroll_run_retry_strategy;
        EXCEPTION WHEN undefined_object THEN NULL; END $$;
    """)

    op.execute("""
        ALTER TABLE payroll_run
            ADD CONSTRAINT ck_payroll_run_retry_strategy
            CHECK (retry_strategy IN ('PER_EMPLOYEE', 'FULL_RUN'));
    """)
