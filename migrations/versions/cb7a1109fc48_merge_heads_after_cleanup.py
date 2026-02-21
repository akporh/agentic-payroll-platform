"""merge heads after cleanup

Revision ID: cb7a1109fc48
Revises: c4bdcbd77c48, ea05e71efbd7
Create Date: 2026-02-19 09:23:05.695025

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb7a1109fc48'
down_revision: Union[str, Sequence[str], None] = ('c4bdcbd77c48', 'ea05e71efbd7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
