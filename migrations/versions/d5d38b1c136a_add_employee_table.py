"""add employee table

Revision ID: d5d38b1c136a
Revises: 9374f9e47d56
Create Date: 2026-02-13 11:23:50.794119

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5d38b1c136a'
down_revision: Union[str, Sequence[str], None] = '9374f9e47d56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
