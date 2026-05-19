"""Merge all divergent heads into a single linear chain

Revision ID: f0a1b2c3d4e5
Revises: a2b3c4d5e6f7, c0d1e2f3a4b5, e6f7a8b9c0d1, ee5ff6aa7bb8
Create Date: 2026-05-18 00:00:00.000000

Resolves multiple heads created by parallel migration branches.
No schema changes — merge-only.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "f0a1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = (
    "a2b3c4d5e6f7",
    "c0d1e2f3a4b5",
    "e6f7a8b9c0d1",
    "ee5ff6aa7bb8",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
