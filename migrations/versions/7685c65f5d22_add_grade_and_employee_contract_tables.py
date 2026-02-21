"""add grade and employee_contract tables

Revision ID: 7685c65f5d22
Revises: 5aa34350e00f
Create Date: 2026-02-17 19:47:04.805081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7685c65f5d22'
down_revision: Union[str, Sequence[str], None] = '5aa34350e00f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
