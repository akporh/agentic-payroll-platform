"""Add resolution fields to payroll_reconciliation

Revision ID: f7a8b9c0d1e2
Revises: e6f7a8b9c0d1
Create Date: 2026-04-08 00:05:00.000000

Adds notes, resolved_by, and resolved_at columns so operators can close a
MISMATCH with an audit trail. Introduces a new RESOLVED status distinct from
MATCHED so the invariant "MATCHED → totals equal" is preserved.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f7a8b9c0d1e2"
down_revision: Union[str, None] = "d0e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("payroll_reconciliation", sa.Column("notes", sa.Text(), nullable=True))
    op.add_column("payroll_reconciliation", sa.Column("resolved_by", sa.String(255), nullable=True))
    op.add_column("payroll_reconciliation", sa.Column("resolved_at", sa.DateTime(), nullable=True))

    # Expand the status enum to include RESOLVED.
    # RESOLVED = operator closed a MISMATCH; totals may still differ.
    # MATCHED  = system-verified; actual_total == expected_total (invariant preserved).
    # The existing chk_matched_totals_equal and chk_mismatch_totals_differ constraints
    # use conditional logic (status <> 'MATCHED' OR ...) so they already safely pass
    # for RESOLVED rows — no need to drop them.
    op.execute("ALTER TABLE payroll_reconciliation DROP CONSTRAINT IF EXISTS chk_reconciliation_status")
    op.execute(
        "ALTER TABLE payroll_reconciliation ADD CONSTRAINT chk_reconciliation_status "
        "CHECK (status IN ('PENDING', 'MATCHED', 'MISMATCH', 'RESOLVED'))"
    )

    # Enforce audit fields are populated when a record is resolved.
    op.execute(
        "ALTER TABLE payroll_reconciliation ADD CONSTRAINT chk_resolved_audit_fields "
        "CHECK (status <> 'RESOLVED' OR "
        "(resolved_by IS NOT NULL AND resolved_at IS NOT NULL))"
    )


def downgrade() -> None:
    # Pre-check: warn operator if RESOLVED rows exist — downgrading will drop
    # the notes/resolved_by/resolved_at audit data for those rows.
    # This is a data-loss warning, not a hard block, so emergency rollbacks
    # remain possible. Log the count so the operator can archive if needed.
    op.execute("""
        DO $$
        DECLARE v_count integer;
        BEGIN
            SELECT COUNT(*) INTO v_count
            FROM payroll_reconciliation
            WHERE status = 'RESOLVED';
            IF v_count > 0 THEN
                RAISE WARNING
                    'Downgrading f7a8b9c0d1e2: % RESOLVED row(s) exist. '
                    'The notes/resolved_by/resolved_at columns will be dropped. '
                    'Archive these rows before proceeding if audit data must be retained.',
                    v_count;
            END IF;
        END $$;
    """)

    op.execute("ALTER TABLE payroll_reconciliation DROP CONSTRAINT IF EXISTS chk_resolved_audit_fields")
    op.execute("ALTER TABLE payroll_reconciliation DROP CONSTRAINT IF EXISTS chk_reconciliation_status")
    op.execute(
        "ALTER TABLE payroll_reconciliation ADD CONSTRAINT chk_reconciliation_status "
        "CHECK (status IN ('PENDING', 'MATCHED', 'MISMATCH'))"
    )
    op.drop_column("payroll_reconciliation", "resolved_at")
    op.drop_column("payroll_reconciliation", "resolved_by")
    op.drop_column("payroll_reconciliation", "notes")
