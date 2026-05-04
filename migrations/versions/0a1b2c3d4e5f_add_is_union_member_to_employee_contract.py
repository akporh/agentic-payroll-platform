"""Add is_union_member to employee_contract — Sprint 13 M3

Revision ID: 0a1b2c3d4e5f
Revises: d6e7f8a9b0c1
Create Date: 2026-05-04 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = "0a1b2c3d4e5f"
down_revision: Union[str, Sequence[str], None] = "d6e7f8a9b0c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    DO $$ BEGIN
        ALTER TABLE employee_contract
        ADD COLUMN is_union_member BOOLEAN NOT NULL DEFAULT FALSE;
    EXCEPTION WHEN duplicate_column THEN NULL;
    END $$;
    """)


def downgrade() -> None:
    op.execute("""
    DO $$
    DECLARE union_count INT;
    BEGIN
        SELECT COUNT(*) INTO union_count
        FROM employee_contract
        WHERE is_union_member = TRUE;

        IF union_count > 0 THEN
            RAISE EXCEPTION
                'cannot remove is_union_member: % rows have is_union_member = TRUE',
                union_count;
        END IF;

        ALTER TABLE employee_contract DROP COLUMN IF EXISTS is_union_member;
    END $$;
    """)
