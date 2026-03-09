"""Add payroll_reconciliation table

Revision ID: d1e2f3a4b5c6
Revises: c3d4e5f6a7b8
Create Date: 2026-03-06

Introduces the payroll_reconciliation table that supports Phase 1 manual
payment reconciliation.  In Phase 1 money movement is handled externally;
this table records whether the amount actually paid matches the system total.

Table: payroll_reconciliation
------------------------------
id               UUID PK        Surrogate key.
payroll_run_id   UUID FK        References payroll_run(payroll_run_id).
expected_total   NUMERIC(18,2)  Total net pay produced by the payroll engine.
actual_total     NUMERIC(18,2)  Amount confirmed paid externally (NULL = pending).
status           TEXT           PENDING | MATCHED | MISMATCH.
reconciled_at    TIMESTAMP      Set when status transitions from PENDING.
created_at       TIMESTAMP      Row creation time (default now()).

Constraints
-----------
uq_reconciliation_run
    UNIQUE (payroll_run_id) — one reconciliation record per run.

chk_reconciliation_status
    status IN ('PENDING', 'MATCHED', 'MISMATCH')

chk_matched_totals_equal
    IF status = 'MATCHED' THEN actual_total = expected_total
    Expressed as: status <> 'MATCHED' OR actual_total = expected_total

chk_mismatch_totals_differ
    IF status = 'MISMATCH' THEN actual_total <> expected_total
    Expressed as: status <> 'MISMATCH' OR actual_total <> expected_total
"""

from typing import Sequence, Union

from alembic import op


revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE payroll_reconciliation (
            id               UUID        NOT NULL DEFAULT gen_random_uuid(),
            payroll_run_id   UUID        NOT NULL
                                         REFERENCES payroll_run(payroll_run_id),
            expected_total   NUMERIC(18,2) NOT NULL,
            actual_total     NUMERIC(18,2),
            status           TEXT        NOT NULL,
            reconciled_at    TIMESTAMP,
            created_at       TIMESTAMP   NOT NULL DEFAULT now(),

            CONSTRAINT pk_payroll_reconciliation
                PRIMARY KEY (id),

            CONSTRAINT uq_reconciliation_run
                UNIQUE (payroll_run_id),

            CONSTRAINT chk_reconciliation_status
                CHECK (status IN ('PENDING', 'MATCHED', 'MISMATCH')),

            CONSTRAINT chk_matched_totals_equal
                CHECK (status <> 'MATCHED' OR actual_total = expected_total),

            CONSTRAINT chk_mismatch_totals_differ
                CHECK (status <> 'MISMATCH' OR actual_total <> expected_total)
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS payroll_reconciliation;")
