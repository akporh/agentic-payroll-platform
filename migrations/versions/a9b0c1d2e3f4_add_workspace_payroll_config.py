"""Add workspace_payroll_config table (PH-6) — versioned-row pattern

Revision ID: a9b0c1d2e3f4
Revises: f8a9b0c1d2e3
Create Date: 2026-04-13

Arch-council: effective_from required (versioned-row pattern).
One workspace may have multiple config rows; the active row is the one
with the greatest effective_from <= CURRENT_DATE.

"""
from typing import Sequence, Union

from alembic import op


revision: str = "a9b0c1d2e3f4"
down_revision: Union[str, Sequence[str], None] = "f8a9b0c1d2e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS workspace_payroll_config (
            config_id               UUID        NOT NULL DEFAULT gen_random_uuid(),
            workspace_id            UUID        NOT NULL REFERENCES workspace(workspace_id),
            effective_from          DATE        NOT NULL DEFAULT CURRENT_DATE,
            ph_mode                 TEXT        NOT NULL DEFAULT 'FILE_BASED',
            ph_rate_code            TEXT        NOT NULL DEFAULT 'OT005',
            saturday_ph_rule        TEXT        NOT NULL DEFAULT 'PH_TAKES_PRECEDENCE',
            sunday_ph_rule          TEXT        NOT NULL DEFAULT 'PH_TAKES_PRECEDENCE',
            d3_leave_overlap_rule   TEXT        NOT NULL DEFAULT 'LEAVE_ABSORBS_PH',
            d4_absence_rule         TEXT        NOT NULL DEFAULT 'ABSENT_IS_DEDUCTIBLE',
            updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_by              UUID,

            CONSTRAINT pk_workspace_payroll_config      PRIMARY KEY (config_id),
            CONSTRAINT uq_workspace_payroll_config      UNIQUE (workspace_id, effective_from),
            CONSTRAINT ck_wpc_ph_mode                   CHECK (ph_mode IN ('AUTOMATIC', 'FILE_BASED')),
            CONSTRAINT ck_wpc_sat_rule                  CHECK (saturday_ph_rule IN ('PH_TAKES_PRECEDENCE', 'DAY_OF_WEEK_TAKES_PRECEDENCE')),
            CONSTRAINT ck_wpc_sun_rule                  CHECK (sunday_ph_rule IN ('PH_TAKES_PRECEDENCE', 'DAY_OF_WEEK_TAKES_PRECEDENCE')),
            CONSTRAINT ck_wpc_d3                        CHECK (d3_leave_overlap_rule IN ('LEAVE_ABSORBS_PH', 'PH_ADDITIVE')),
            CONSTRAINT ck_wpc_d4                        CHECK (d4_absence_rule IN ('ABSENT_IS_DEDUCTIBLE', 'PH_EXCUSES_ABSENCE'))
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS workspace_payroll_config;")
