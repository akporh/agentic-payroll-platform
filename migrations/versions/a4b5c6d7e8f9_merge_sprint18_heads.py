"""Merge Sprint 18 heads into single head before Sprint 19 snapshot tables.

Revision ID: a4b5c6d7e8f9
Revises: b6c7d8e9f0a1, c9d0e1f2a3b4, d8e9f0a1b2c3, e9f0a1b2c3d4, f2a3b4c5d6e7, f7a1b2c3d4e5
Create Date: 2026-06-01
"""

from alembic import op

revision: str = "a4b5c6d7e8f9"
down_revision = (
    "b6c7d8e9f0a1",
    "c9d0e1f2a3b4",
    "d8e9f0a1b2c3",
    "e9f0a1b2c3d4",
    "f2a3b4c5d6e7",
    "f7a1b2c3d4e5",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
