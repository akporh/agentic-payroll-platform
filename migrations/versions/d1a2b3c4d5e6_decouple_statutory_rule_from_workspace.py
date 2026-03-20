"""decouple_statutory_rule_from_workspace

Revision ID: d1a2b3c4d5e6
Revises: 4c5d6e7f8a9b, c1d2e3f4a5b6
Create Date: 2026-03-19 00:00:00.000000

statutory_rule is platform-level data shared across all workspaces in a country.
Removes the direct FK from workspace to statutory_rule so the engine resolves
the applicable rule at runtime via statutory_rule.country_code + version DESC.
"""
from typing import Sequence, Union
from alembic import op


revision: str = 'd1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = ('4c5d6e7f8a9b', 'c1d2e3f4a5b6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint('workspace_statutory_rule_id_fkey', 'workspace', type_='foreignkey')
    op.drop_column('workspace', 'statutory_rule_id')


def downgrade():
    import sqlalchemy as sa
    from sqlalchemy.dialects.postgresql import UUID
    op.add_column(
        'workspace',
        sa.Column('statutory_rule_id', UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        'workspace_statutory_rule_id_fkey',
        'workspace', 'statutory_rule',
        ['statutory_rule_id'], ['statutory_rule_id'],
    )
