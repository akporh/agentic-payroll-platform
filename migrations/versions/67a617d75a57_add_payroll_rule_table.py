"""add payroll_rule table

Revision ID: 67a617d75a57
Revises: 94a312394013
Create Date: 2026-02-14 04:58:11.699072

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67a617d75a57'
down_revision: Union[str, Sequence[str], None] = '94a312394013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payroll_rule",
        sa.Column("payroll_rule_id", sa.UUID(), primary_key=True),
        sa.Column("workspace_id", sa.UUID(),
                  sa.ForeignKey("workspace.workspace_id"),
                  nullable=False),

        sa.Column("rule_name", sa.String(), nullable=False),
        sa.Column("rule_logic_jsonb", sa.JSON(), nullable=False),

        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
    )
def downgrade() -> None:
    op.drop_table("payroll_rule")

