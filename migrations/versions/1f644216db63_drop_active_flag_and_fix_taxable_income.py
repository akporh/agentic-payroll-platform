"""drop redundant active flag and fix TAXABLE_INCOME metadata

- Drop component_metadata.active (redundant with is_active)
- Set component_class and calculation_method for TAXABLE_INCOME (NG)

Revision ID: 1f644216db63
Revises: b3363ecdb054
Create Date: 2026-03-16

"""
from alembic import op

revision = '1f644216db63'
down_revision = 'b3363ecdb054'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('component_metadata', 'active')

    op.execute("""
        UPDATE component_metadata
        SET component_class    = 'aggregate',
            calculation_method = 'taxable_income'
        WHERE component_code = 'TAXABLE_INCOME'
          AND country_code   = 'NG'
    """)


def downgrade():
    import sqlalchemy as sa
    op.add_column(
        'component_metadata',
        sa.Column('active', sa.Boolean(), nullable=False, server_default='TRUE'),
    )

    op.execute("""
        UPDATE component_metadata
        SET component_class    = NULL,
            calculation_method = NULL
        WHERE component_code = 'TAXABLE_INCOME'
          AND country_code   = 'NG'
    """)
