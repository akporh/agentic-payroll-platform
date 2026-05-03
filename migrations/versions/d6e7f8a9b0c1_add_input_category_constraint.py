"""Add CHECK constraint to payroll_input.input_category for M2 (PAYE_ONLY path).

Sprint 12 M2 arch-council binding decision D-M2-1:
  - Casing is uppercase throughout. Existing values EARNING/DEDUCTION are retained unchanged.
  - New allowed values: STANDARD, PAYE_ONLY.
  - Migration: pre-check for unknown values, then ADD CONSTRAINT only (no row UPDATE needed).

Revision ID: d6e7f8a9b0c1
Revises: c5d6e7f8a9b0
Create Date: 2026-05-03 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision: str = "d6e7f8a9b0c1"
down_revision: str = "c5d6e7f8a9b0"
branch_labels = None
depends_on = None

_ALLOWED_CATEGORIES = ("EARNING", "DEDUCTION", "STANDARD", "PAYE_ONLY")


def upgrade() -> None:
    conn = op.get_bind()

    # Pre-check: abort if any live input_category value is outside the allowed set.
    placeholders = ", ".join(f"'{v}'" for v in _ALLOWED_CATEGORIES)
    result = conn.execute(sa.text(
        f"SELECT DISTINCT input_category FROM payroll_input "
        f"WHERE input_category IS NOT NULL AND input_category NOT IN ({placeholders})"
    ))
    violations = [row[0] for row in result]
    if violations:
        raise RuntimeError(
            f"Migration aborted: payroll_input contains unrecognised input_category "
            f"values {violations!r}. Clean up these rows before applying this migration."
        )

    # Add CHECK constraint.
    op.execute(sa.text(
        """
        DO $$ BEGIN
            ALTER TABLE payroll_input
                ADD CONSTRAINT ck_payroll_input_category
                CHECK (input_category IN ('EARNING', 'DEDUCTION', 'STANDARD', 'PAYE_ONLY'));
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
        """
    ))


def downgrade() -> None:
    op.execute(sa.text(
        """
        DO $$ BEGIN
            ALTER TABLE payroll_input DROP CONSTRAINT ck_payroll_input_category;
        EXCEPTION WHEN undefined_object THEN NULL;
        END $$
        """
    ))
