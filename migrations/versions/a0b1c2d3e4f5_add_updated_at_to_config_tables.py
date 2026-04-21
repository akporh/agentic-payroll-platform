"""add updated_at to grade, designation, salary_definition, payroll_rule, pay_cycle

Revision ID: a0b1c2d3e4f5
Revises: f9a0b1c2d3e4
Create Date: 2026-04-20

"""

from alembic import op

revision: str = "a0b1c2d3e4f5"
down_revision: str = "f9a0b1c2d3e4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ("grade", "designation", "salary_definition", "payroll_rule", "pay_cycle"):
        op.execute(f"""
            DO $$ BEGIN
                ALTER TABLE {table} ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
            EXCEPTION WHEN duplicate_column THEN NULL;
            END $$;
        """)


def downgrade() -> None:
    for table in ("grade", "designation", "salary_definition", "payroll_rule", "pay_cycle"):
        op.execute(f"""
            DO $$ BEGIN
                ALTER TABLE {table} DROP COLUMN IF EXISTS updated_at;
            EXCEPTION WHEN undefined_column THEN NULL;
            END $$;
        """)
