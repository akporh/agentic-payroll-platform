"""Add updated_at to client_component_metadata (D-ARCH-3 audit gap)

Revision ID: 26b848abab55
Revises: a0b1c2d3e4f5
Create Date: 2026-04-21
"""

from alembic import op

revision: str = "26b848abab55"
down_revision: str = "a0b1c2d3e4f5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE client_component_metadata
                ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)


def downgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE client_component_metadata DROP COLUMN IF EXISTS updated_at;
        EXCEPTION WHEN undefined_column THEN NULL;
        END $$;
    """)
