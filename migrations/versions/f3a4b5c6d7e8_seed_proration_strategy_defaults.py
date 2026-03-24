"""Seed default proration strategies into earning component metadata.

Adds calculations_behaviour.proration_strategy to the metadata_json of
each earning (salary_component) component in the global component_metadata
table for Nigeria.

This seeds the global defaults consumed by the two-layer proration system:
  Layer 1 (workspace): client_component_metadata.overrides_json
  Layer 2 (global):    component_metadata.metadata_json   ← this migration

Engine reads: workspace override → fall back to global default → skip.

Revision ID: f3a4b5c6d7e8
Revises: e2a3b4c5d6f7
Create Date: 2026-03-24
"""

from typing import Sequence, Union
from alembic import op

revision: str = "f3a4b5c6d7e8"
down_revision: Union[str, Sequence[str], None] = "e2a3b4c5d6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # BASIC salary is earned for working days (Mon–Fri).
    op.execute("""
        UPDATE component_metadata
        SET metadata_json = jsonb_set(
            metadata_json,
            '{calculations_behaviour}',
            '{"proration_strategy": "work_days"}',
            true
        )
        WHERE component_code = 'BASIC'
          AND country_code   = 'NG';
    """)

    # HOUSING, TRANSPORT and CONSOLIDATED_ALLOWANCE accrue every calendar day
    # (rent and commute costs are not working-day dependent).
    op.execute("""
        UPDATE component_metadata
        SET metadata_json = jsonb_set(
            metadata_json,
            '{calculations_behaviour}',
            '{"proration_strategy": "calendar_days"}',
            true
        )
        WHERE component_code IN ('HOUSING', 'TRANSPORT', 'CONSOLIDATED_ALLOWANCE')
          AND country_code   = 'NG';
    """)


def downgrade() -> None:
    op.execute("""
        UPDATE component_metadata
        SET metadata_json = metadata_json - 'calculations_behaviour'
        WHERE component_code IN ('BASIC', 'HOUSING', 'TRANSPORT', 'CONSOLIDATED_ALLOWANCE')
          AND country_code   = 'NG';
    """)
