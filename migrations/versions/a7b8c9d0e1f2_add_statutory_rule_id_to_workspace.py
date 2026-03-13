"""add_statutory_rule_id_to_workspace

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-03-12 00:00:00.000000

Adds a direct FK from workspace to statutory_rule so the payroll engine
can look up tax bands without a fragile country-code → authority-name
mapping (workspace.country_code='NG' never matched statutory_rule.state='FIRS').

Changes
-------
1. Add workspace.statutory_rule_id (nullable UUID FK → statutory_rule).
2. Backfill ACME Airforce workspace with the latest FIRS rule.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, Sequence[str], None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # ------------------------------------------------------------------
    # 1. Add nullable FK column
    # ------------------------------------------------------------------
    op.add_column(
        'workspace',
        sa.Column(
            'statutory_rule_id',
            UUID(as_uuid=True),
            sa.ForeignKey('statutory_rule.statutory_rule_id'),
            nullable=True,
        ),
    )

    # ------------------------------------------------------------------
    # 2. Backfill ACME Airforce with the latest FIRS statutory rule
    # ------------------------------------------------------------------
    op.execute("""
        UPDATE workspace
        SET statutory_rule_id = (
            SELECT statutory_rule_id
            FROM   statutory_rule
            WHERE  state = 'FIRS'
            ORDER  BY version DESC
            LIMIT  1
        )
        WHERE workspace_id = '8d14e7a1-5f68-4f46-b01d-b2622b53bc18';
    """)


def downgrade():
    op.drop_column('workspace', 'statutory_rule_id')
