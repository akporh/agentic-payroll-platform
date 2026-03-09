"""Persist payroll totals on payroll_run

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-04

Ensures payroll_run stores accurate financial totals that can be used for
Phase 1 reconciliation (payroll_result rows vs payroll_run summary).

Changes
-------
1. Backfill existing NULLs to 0 for columns added in 9ffee63ba8d1:
   - total_gross_pay, total_deduction, total_net_pay

2. Strengthen those columns to NUMERIC(18,2) NOT NULL DEFAULT 0:
   - Precision NUMERIC(18,2): up to 16 integer digits + 2 decimal places,
     sufficient for NGN payroll at any scale.
   - NOT NULL: prevents silent omissions in future persistence code.
   - DEFAULT 0: safe insert without explicit value during rollout.

3. New column: total_tax NUMERIC(18,2) NOT NULL DEFAULT 0
   Stores the total PAYE tax deducted across all employees in the run.
   Semantically equivalent to total_deduction (which stores the same figure)
   but uses the domain term "tax" for clarity in reconciliation queries.

Phase 2 note
------------
payroll_payment_instruction is NOT created in this migration.
Automated payment instructions are a Phase 2 concern; money movement in
Phase 1 is handled manually outside this system.
"""

from typing import Sequence, Union

from alembic import op


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Backfill existing NULLs so NOT NULL constraints can be applied
    # ------------------------------------------------------------------
    op.execute("""
        UPDATE payroll_run
        SET total_gross_pay = 0
        WHERE total_gross_pay IS NULL;
    """)

    op.execute("""
        UPDATE payroll_run
        SET total_deduction = 0
        WHERE total_deduction IS NULL;
    """)

    op.execute("""
        UPDATE payroll_run
        SET total_net_pay = 0
        WHERE total_net_pay IS NULL;
    """)

    # ------------------------------------------------------------------
    # 2. Strengthen total_gross_pay to NUMERIC(18,2) NOT NULL DEFAULT 0
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE payroll_run
        ALTER COLUMN total_gross_pay TYPE NUMERIC(18,2)
            USING total_gross_pay::NUMERIC(18,2);
    """)
    op.execute("""
        ALTER TABLE payroll_run
        ALTER COLUMN total_gross_pay SET NOT NULL;
    """)
    op.execute("""
        ALTER TABLE payroll_run
        ALTER COLUMN total_gross_pay SET DEFAULT 0;
    """)

    # ------------------------------------------------------------------
    # 3. Strengthen total_deduction to NUMERIC(18,2) NOT NULL DEFAULT 0
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE payroll_run
        ALTER COLUMN total_deduction TYPE NUMERIC(18,2)
            USING total_deduction::NUMERIC(18,2);
    """)
    op.execute("""
        ALTER TABLE payroll_run
        ALTER COLUMN total_deduction SET NOT NULL;
    """)
    op.execute("""
        ALTER TABLE payroll_run
        ALTER COLUMN total_deduction SET DEFAULT 0;
    """)

    # ------------------------------------------------------------------
    # 4. Strengthen total_net_pay to NUMERIC(18,2) NOT NULL DEFAULT 0
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE payroll_run
        ALTER COLUMN total_net_pay TYPE NUMERIC(18,2)
            USING total_net_pay::NUMERIC(18,2);
    """)
    op.execute("""
        ALTER TABLE payroll_run
        ALTER COLUMN total_net_pay SET NOT NULL;
    """)
    op.execute("""
        ALTER TABLE payroll_run
        ALTER COLUMN total_net_pay SET DEFAULT 0;
    """)

    # ------------------------------------------------------------------
    # 5. New column: total_tax (PAYE tax total, domain alias for deduction)
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE payroll_run
        ADD COLUMN IF NOT EXISTS total_tax NUMERIC(18,2) NOT NULL DEFAULT 0;
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE payroll_run DROP COLUMN IF EXISTS total_tax;")

    # Revert to plain NUMERIC (nullable) — matches state after 9ffee63ba8d1
    op.execute("""
        ALTER TABLE payroll_run
        ALTER COLUMN total_net_pay DROP NOT NULL,
        ALTER COLUMN total_net_pay DROP DEFAULT,
        ALTER COLUMN total_net_pay TYPE NUMERIC;
    """)
    op.execute("""
        ALTER TABLE payroll_run
        ALTER COLUMN total_deduction DROP NOT NULL,
        ALTER COLUMN total_deduction DROP DEFAULT,
        ALTER COLUMN total_deduction TYPE NUMERIC;
    """)
    op.execute("""
        ALTER TABLE payroll_run
        ALTER COLUMN total_gross_pay DROP NOT NULL,
        ALTER COLUMN total_gross_pay DROP DEFAULT,
        ALTER COLUMN total_gross_pay TYPE NUMERIC;
    """)
