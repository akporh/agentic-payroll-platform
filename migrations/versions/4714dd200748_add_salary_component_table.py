"""add salary_component table

Revision ID: 4714dd200748
Revises: d5d38b1c136a
Create Date: 2026-02-13 11:29:14.554158

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4714dd200748'
down_revision: Union[str, Sequence[str], None] = 'd5d38b1c136a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
