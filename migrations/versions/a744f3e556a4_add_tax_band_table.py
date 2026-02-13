"""add tax_band table

Revision ID: a744f3e556a4
Revises: dd26843b5e36
Create Date: 2026-02-13 12:29:04.357900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a744f3e556a4'
down_revision: Union[str, Sequence[str], None] = 'dd26843b5e36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tax_band",
        sa.Column("tax_band_id", sa.UUID(), primary_key=True),
        sa.Column("statutory_rule_id", sa.UUID(),
                  sa.ForeignKey("statutory_rule.statutory_rule_id"),
                  nullable=False),

        sa.Column("band_order", sa.Integer(), nullable=False),
        sa.Column("lower_limit", sa.Numeric(), nullable=False),
        sa.Column("upper_limit", sa.Numeric(), nullable=True),
        sa.Column("rate", sa.Numeric(), nullable=False),
    )

    op.create_index(
        "ix_tax_band_rule_order",
        "tax_band",
        ["statutory_rule_id", "band_order"],
        unique=True,
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_tax_band_rule_order", table_name="tax_band")
    op.drop_table("tax_band")
