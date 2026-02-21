"""merge heads

Revision ID: 5ce90b326db6
Revises: 7685c65f5d2, 7685c65f5d22
Create Date: 2026-02-17 20:01:19.752483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ce90b326db6'
down_revision: Union[str, Sequence[str], None] = ('7685c65f5d2', '7685c65f5d22')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
