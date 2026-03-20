"""seed NG earning component metadata

BASIC, HOUSING, TRANSPORT, and CONSOLIDATED_ALLOWANCE exist only in
client_component_metadata (workspace overrides).  The sequential executor
needs global component_metadata entries for all components so it can look
up component_class, calculation_method, and execution_priority in one place.

This migration inserts the four earning components into component_metadata
for country_code='NG'.

Revision ID: 8d2b70219b84
Revises: e1f2a3b4c5d6
Create Date: 2026-03-16

"""
from alembic import op
import sqlalchemy as sa

revision = '8d2b70219b84'
down_revision = 'e1f2a3b4c5d6'
branch_labels = None
depends_on = None

# Fixed UUIDs so the migration is idempotent on re-run in fresh envs
_EARNING_COMPONENTS = [
    {
        "id":                 "a0000001-0000-0000-0000-000000000001",
        "component_code":     "BASIC",
        "component_class":    "earning",
        "calculation_method": "salary_component",
        "execution_priority": 10,
    },
    {
        "id":                 "a0000001-0000-0000-0000-000000000002",
        "component_code":     "HOUSING",
        "component_class":    "earning",
        "calculation_method": "salary_component",
        "execution_priority": 20,
    },
    {
        "id":                 "a0000001-0000-0000-0000-000000000003",
        "component_code":     "TRANSPORT",
        "component_class":    "earning",
        "calculation_method": "salary_component",
        "execution_priority": 30,
    },
    {
        "id":                 "a0000001-0000-0000-0000-000000000004",
        "component_code":     "CONSOLIDATED_ALLOWANCE",
        "component_class":    "earning",
        "calculation_method": "salary_component",
        "execution_priority": 40,
    },
]


def upgrade():
    for c in _EARNING_COMPONENTS:
        op.execute(sa.text("""
            INSERT INTO component_metadata (
                component_metadata_id,
                component_code,
                country_code,
                version,
                metadata_json,
                effective_from,
                is_active,
                component_class,
                calculation_method,
                execution_priority
            ) VALUES (
                :id,
                :component_code,
                'NG',
                1,
                :metadata_json,
                '2024-01-01',
                TRUE,
                :component_class,
                :calculation_method,
                :execution_priority
            )
            ON CONFLICT (component_code, country_code, version) DO UPDATE
                SET component_class    = EXCLUDED.component_class,
                    calculation_method = EXCLUDED.calculation_method,
                    execution_priority = EXCLUDED.execution_priority
        """).bindparams(
            id=c["id"],
            component_code=c["component_code"],
            metadata_json='{"category": "earning", "gross_effect": "increase", "is_taxable": true, "is_pensionable": true, "is_proratable": true}',
            component_class=c["component_class"],
            calculation_method=c["calculation_method"],
            execution_priority=c["execution_priority"],
        ))


def downgrade():
    for c in _EARNING_COMPONENTS:
        op.execute(sa.text("""
            DELETE FROM component_metadata
            WHERE component_code          = :component_code
              AND country_code            = 'NG'
              AND version                 = 1
              AND component_metadata_id   = :id
        """).bindparams(
            component_code=c["component_code"],
            id=c["id"],
        ))
