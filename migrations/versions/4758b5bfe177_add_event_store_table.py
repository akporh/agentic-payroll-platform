"""add event_store table

Revision ID: 4758b5bfe177
Revises: 76566966d3b3
Create Date: 2026-02-13 13:08:57.514324

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4758b5bfe177'
down_revision: Union[str, Sequence[str], None] = '76566966d3b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "event_store",
        sa.Column("event_id", sa.UUID(), primary_key=True),
        sa.Column("workspace_id", sa.UUID(),
                  sa.ForeignKey("workspace.workspace_id"),
                  nullable=False),

        sa.Column("aggregate_id", sa.UUID(), nullable=False),
        sa.Column("aggregate_type", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),

        sa.Column("event_payload", sa.JSON(), nullable=False),
        sa.Column("actor_user_id", sa.UUID(), nullable=True),

        sa.Column("occurred_at", sa.TIMESTAMP(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("event_store")

