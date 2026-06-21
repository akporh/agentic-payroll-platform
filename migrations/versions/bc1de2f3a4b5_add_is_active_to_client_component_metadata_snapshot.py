"""add is_active to client_component_metadata_snapshot

Revision ID: bc1de2f3a4b5
Revises: ab1c2d3e4f50
Create Date: 2026-06-18

The payroll retry path reads component enable/disable state from the snapshot.
Without is_active persisted at snapshot time, a CORRECTION run cannot know
which components were disabled when the original run was created — causing
divergence between the original result and the correction.
"""

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = "bc1de2f3a4b5"
down_revision: Union[str, Sequence[str], None] = "ab1c2d3e4f50"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE client_component_metadata_snapshot
                ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE client_component_metadata_snapshot
            DROP COLUMN IF EXISTS is_active;
    """)
