"""add_workspace_status

Revision ID: b2e7a07972b7
Revises: 695bcbcc42f3
Create Date: 2026-03-03 04:15:47.387425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2e7a07972b7'
down_revision: Union[str, Sequence[str], None] = '695bcbcc42f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():

    # 1️⃣ Create ENUM
    op.execute("""
    CREATE TYPE workspace_status AS ENUM (
        'DRAFT',
        'STRUCTURE_DEFINED',
        'COMPENSATION_DEFINED',
        'RULES_DEFINED',
        'READY',
        'LIVE'
    );
    """)

    # 2️⃣ Drop existing default
    op.execute("""
    ALTER TABLE workspace
    ALTER COLUMN status DROP DEFAULT;
    """)

    # 3️⃣ Convert column type
    op.execute("""
    ALTER TABLE workspace
    ALTER COLUMN status
    TYPE workspace_status
    USING status::workspace_status;
    """)

    # 4️⃣ Re-add default (now as ENUM)
    op.execute("""
    ALTER TABLE workspace
    ALTER COLUMN status
    SET DEFAULT 'DRAFT';
    """)

def downgrade() -> None:
    """Downgrade schema."""
    pass
