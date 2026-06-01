"""MIG-18-E: CHECK constraint on client_component_metadata.proration_strategy

Revision ID: f2a3b4c5d6e7
Revises: f0a1b2c3d4e5
Create Date: 2026-05-31 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op

revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, Sequence[str], None] = "f0a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE client_component_metadata
                ADD CONSTRAINT chk_ccm_proration_strategy
                CHECK (proration_strategy IN ('work_days', 'calendar_days', 'fixed_30'));
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE client_component_metadata
            DROP CONSTRAINT IF EXISTS chk_ccm_proration_strategy;
    """)
