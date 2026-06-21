"""seed TAXABLE_INCOME into component_metadata

Revision ID: cd2ef3a4b5c6
Revises: bc1de2f3a4b5
Create Date: 2026-06-19

TAXABLE_INCOME was missing from component_metadata, causing the sequential
executor to skip the taxable_income step. PAYE then received 0 as input and
calculated ₦0.00 for every employee.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision: str = "cd2ef3a4b5c6"
down_revision: str = "bc1de2f3a4b5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(text("""
        INSERT INTO component_metadata
            (component_metadata_id, country_code, version, component_code,
             component_class, calculation_method, execution_priority,
             is_active, effective_from, metadata_json)
        VALUES
            (gen_random_uuid(), 'NG', 1, 'TAXABLE_INCOME', 'aggregate',
             'taxable_income', 300, true, '2026-01-01',
             '{"deduct_components": ["PENSION_EMPLOYEE", "RENT_RELIEF"], "engine_behavior": {"derived_node": true}}'::jsonb)
        ON CONFLICT (component_code, country_code, version) DO NOTHING
    """))


def downgrade() -> None:
    op.execute(text("""
        DELETE FROM component_metadata
        WHERE component_code = 'TAXABLE_INCOME'
          AND country_code = 'NG'
          AND version = 1
    """))
