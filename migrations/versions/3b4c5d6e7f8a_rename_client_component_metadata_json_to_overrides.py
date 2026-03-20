"""rename client_component_metadata.metadata_json to overrides_json

client_component_metadata rows do not need to carry the full platform
metadata shape. They only need to hold the keys a workspace wants to
change. Renaming the column makes this intent explicit and prevents
callers from assuming it is a full metadata object.

Revision ID: 3b4c5d6e7f8a
Revises: 2a3b4c5d6e7f
Create Date: 2026-03-19
"""
from alembic import op

revision = '3b4c5d6e7f8a'
down_revision = '2a3b4c5d6e7f'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'client_component_metadata',
        'metadata_json',
        new_column_name='overrides_json',
    )


def downgrade():
    op.alter_column(
        'client_component_metadata',
        'overrides_json',
        new_column_name='metadata_json',
    )
