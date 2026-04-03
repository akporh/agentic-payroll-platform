"""add employee_number column (ACME required)

Revision ID: bbca8050dd33
Revises: 6c2ecc683076
Create Date: 2026-02-17 22:37:14.747313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bbca8050dd33'
down_revision: Union[str, Sequence[str], None] = '6c2ecc683076'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass  # employee_number already added in 6c2ecc683076

def downgrade() -> None:
    pass

