"""Add unique constraint on rule_set (workspace_id, effective_from)

Revision ID: a1b2c3d4e5f7
Revises: fe0bad282b7d
Create Date: 2026-04-08 00:00:00.000000

Prevents two rule sets for the same workspace sharing the same effective_from
date, which would produce non-deterministic temporal rule resolution.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "a1b2c3d4e5f7"
down_revision: Union[str, None] = "fe0bad282b7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    DO $$ BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint WHERE conname = 'uq_rule_set_workspace_effective'
        ) THEN
            ALTER TABLE rule_set ADD CONSTRAINT uq_rule_set_workspace_effective
                UNIQUE (workspace_id, effective_from);
        END IF;
    END $$;
    """)


def downgrade() -> None:
    op.execute("""
    DO $$ BEGIN
        IF EXISTS (
            SELECT 1 FROM pg_constraint WHERE conname = 'uq_rule_set_workspace_effective'
        ) THEN
            ALTER TABLE rule_set DROP CONSTRAINT uq_rule_set_workspace_effective;
        END IF;
    END $$;
    """)
