"""add attendance_code_config and attendance_policy_config workspace tables

Revision ID: bb2cc3dd4ee5
Revises: aa1bb2cc3dd4
Create Date: 2026-05-13
"""
from typing import Union, Sequence
from alembic import op

revision: str = "bb2cc3dd4ee5"
down_revision: Union[str, Sequence[str], None] = "aa1bb2cc3dd4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS attendance_code_config (
            attendance_code_config_id UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            workspace_id              UUID        NOT NULL REFERENCES workspace(workspace_id),
            client_code               VARCHAR(20) NOT NULL,
            description               VARCHAR(200),
            category                  VARCHAR(10) NOT NULL
                                      CHECK (category IN ('WORK','LEAVE','OT','SHIFT')),
            is_active                 BOOLEAN     NOT NULL DEFAULT TRUE,
            created_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (workspace_id, client_code)
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS attendance_policy_config (
            attendance_policy_config_id  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            workspace_id                 UUID        NOT NULL REFERENCES workspace(workspace_id),
            client_code                  VARCHAR(20) NOT NULL,
            counts_as_paid               BOOLEAN     NOT NULL DEFAULT TRUE,
            counts_towards_ot_threshold  BOOLEAN     NOT NULL DEFAULT TRUE,
            hours_equivalent             NUMERIC(5,2),
            unit_fraction                NUMERIC(5,4),
            eligible_for_shift_allowance BOOLEAN     NOT NULL DEFAULT FALSE,
            eligible_for_ot              BOOLEAN     NOT NULL DEFAULT FALSE,
            created_at                   TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at                   TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT fk_policy_to_code
                FOREIGN KEY (workspace_id, client_code)
                REFERENCES attendance_code_config (workspace_id, client_code),
            UNIQUE (workspace_id, client_code),
            CHECK (hours_equivalent IS NULL OR hours_equivalent > 0),
            CHECK (unit_fraction IS NULL OR (unit_fraction > 0 AND unit_fraction <= 1)),
            CHECK (NOT (counts_as_paid = FALSE AND counts_towards_ot_threshold = TRUE)),
            CHECK (NOT (hours_equivalent IS NOT NULL AND unit_fraction IS NOT NULL))
        )
    """)

    # Hot path index for derivation loop
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_attendance_policy_config_workspace_code
        ON attendance_policy_config (workspace_id, client_code)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_attendance_policy_config_workspace_code")
    op.execute("DROP TABLE IF EXISTS attendance_policy_config")
    op.execute("DROP TABLE IF EXISTS attendance_code_config")
