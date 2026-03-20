"""component_metadata active column and TAXABLE_INCOME priority

Fix 1: Add active boolean column to component_metadata (distinct from is_active;
        controls participation in the sequential execution pipeline).
Fix 2: Set execution_priority=300 for TAXABLE_INCOME (NG).

Revision ID: b3363ecdb054
Revises: 8d2b70219b84
Create Date: 2026-03-16

"""
from alembic import op
import sqlalchemy as sa

revision = 'b3363ecdb054'
down_revision = '8d2b70219b84'
branch_labels = None
depends_on = None


def upgrade():
    # Fix 1 — add active column
    op.add_column(
        'component_metadata',
        sa.Column('active', sa.Boolean(), nullable=False, server_default='TRUE'),
    )

    # Fix 2 — TAXABLE_INCOME execution priority
    op.execute("""
        UPDATE component_metadata
        SET execution_priority = 300
        WHERE component_code = 'TAXABLE_INCOME'
          AND country_code   = 'NG'
    """)


def downgrade():
    op.execute("""
        UPDATE component_metadata
        SET execution_priority = NULL
        WHERE component_code = 'TAXABLE_INCOME'
          AND country_code   = 'NG'
    """)

    op.drop_column('component_metadata', 'active')
