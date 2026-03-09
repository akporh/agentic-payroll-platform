"""make employee_contract grade_id nullable

Revision ID: d5e6f7a8b9c0
Revises: 0daab4ac893b
Create Date: 2026-03-04

The commit endpoint (POST /onboarding/commit) inserts employee_contract rows
without a grade_id — grade assignment is a separate concern from initial
onboarding. The original NOT NULL constraint on grade_id blocks the entire
onboarding commit flow. Making it nullable unblocks the pipeline.
"""

from typing import Sequence, Union
from alembic import op

revision: str = 'd5e6f7a8b9c0'
down_revision: Union[str, Sequence[str], None] = '0daab4ac893b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        ALTER TABLE employee_contract
        ALTER COLUMN grade_id DROP NOT NULL;
    """)


def downgrade():
    op.execute("""
        ALTER TABLE employee_contract
        ALTER COLUMN grade_id SET NOT NULL;
    """)
