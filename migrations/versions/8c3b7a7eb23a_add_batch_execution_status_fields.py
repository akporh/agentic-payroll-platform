"""add batch execution status fields

Revision ID: 8c3b7a7eb23a
Revises: 6f5b05ff4690


"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c3b7a7eb23a'
down_revision: Union[str, Sequence[str], None] = '6f5b05ff4690'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None 


def upgrade():
    pass

def downgrade():
    pass