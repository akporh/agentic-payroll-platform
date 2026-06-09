"""add imported_grade_label and imported_designation_label to employee_contract

Revision ID: ab1c2d3e4f50
Revises: fe0bad282b7d
Create Date: 2026-06-09

Sprint 23 — EMP-REG-3: Upload decoupling. Store raw Excel grade/designation text
so operators can reference it during the separate Enroll step.
"""

from alembic import op

revision: str = "ab1c2d3e4f50"
down_revision: str = "e7f8a9b0c1d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE employee_contract ADD COLUMN imported_grade_label VARCHAR(100);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$
    """)
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE employee_contract ADD COLUMN imported_designation_label VARCHAR(100);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE employee_contract DROP COLUMN IF EXISTS imported_grade_label")
    op.execute("ALTER TABLE employee_contract DROP COLUMN IF EXISTS imported_designation_label")
