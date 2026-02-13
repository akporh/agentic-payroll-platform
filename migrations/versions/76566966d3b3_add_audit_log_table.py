"""add audit_log table

Revision ID: 76566966d3b3
Revises: a744f3e556a4
Create Date: 2026-02-13 12:52:19.302783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76566966d3b3'
down_revision: Union[str, Sequence[str], None] = 'a744f3e556a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("audit_log_id", sa.UUID(), primary_key=True),
        sa.Column("workspace_id", sa.UUID(),
                  sa.ForeignKey("workspace.workspace_id"),
                  nullable=False),

        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),

        sa.Column("old_value_jsonb", sa.JSON(), nullable=True),
        sa.Column("new_value_jsonb", sa.JSON(), nullable=True),

        sa.Column("performed_by", sa.String(), nullable=False),
        sa.Column("performed_at", sa.DateTime(), server_default=sa.func.now()),
    )



def downgrade() -> None:
    op.drop_table("audit_log")

