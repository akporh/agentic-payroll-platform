"""Add is_active and proration_strategy columns to client_component_metadata.

The existing PATCH /component-overrides/{code} endpoint already writes these
columns via raw SQL. This migration makes the schema match reality.

Revision ID: f9a0b1c2d3e4
Revises: f7a8b9c0d1e2
Create Date: 2026-04-20 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision: str = "f9a0b1c2d3e4"
down_revision: str = "f7a8b9c0d1e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE client_component_metadata
                ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE client_component_metadata
                ADD COLUMN proration_strategy VARCHAR(50);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)


def downgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE client_component_metadata DROP COLUMN IF EXISTS proration_strategy;
        EXCEPTION WHEN others THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE client_component_metadata DROP COLUMN IF EXISTS is_active;
        EXCEPTION WHEN others THEN NULL;
        END $$;
    """)
