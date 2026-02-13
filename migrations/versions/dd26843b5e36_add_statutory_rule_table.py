"""add statutory_rule table

Revision ID: dd26843b5e36
Revises: d6f59caea39f
Create Date: 2026-02-13 12:21:10.616887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd26843b5e36'
down_revision: Union[str, Sequence[str], None] = 'd6f59caea39f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "statutory_rule",
        sa.Column("statutory_rule_id", sa.UUID(), primary_key=True),
        sa.Column("country_code", sa.String(), nullable=False),
        sa.Column("rule_type", sa.String(), nullable=False),
        sa.Column("calculation_logic_jsonb", sa.JSON(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("statutory_rule")

