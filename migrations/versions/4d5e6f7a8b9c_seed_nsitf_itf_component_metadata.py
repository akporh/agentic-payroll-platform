"""Seed NSITF and ITF employer-cost component_metadata — Sprint 13 M5

NSITF_EMPLOYER_COST and ITF_EMPLOYER_COST are employer-side statutory contributions
at 1% each. Both use component_class='employer_cost', which the net_formula handler
explicitly excludes from NET_PAY and TAXABLE_INCOME.

Execution priorities:
  NSITF_EMPLOYER_COST = 460 (after CHECK_OFF_DUES=450)
  ITF_EMPLOYER_COST   = 470 (after NSITF=460)
  NET_PAY             = 500

Rate stored in metadata_json, read by handlers — not hardcoded in Python.
Workspaces opt-in via client_component_metadata.overrides_json['is_active'] = true.

Revision ID: 4d5e6f7a8b9c
Revises: 3c4d5e6f7a8b
Create Date: 2026-05-04 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = "4d5e6f7a8b9c"
down_revision: Union[str, Sequence[str], None] = "3c4d5e6f7a8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_COMPONENTS = [
    {
        "component_code":     "NSITF_EMPLOYER_COST",
        "component_class":    "employer_cost",
        "calculation_method": "nsitf_employer",
        "execution_priority": 460,
        "metadata_json":      '{"rate": "0.01"}'
    },
    {
        "component_code":     "ITF_EMPLOYER_COST",
        "component_class":    "employer_cost",
        "calculation_method": "itf_employer",
        "execution_priority": 470,
        "metadata_json":      '{"rate": "0.01"}'
    },
]


def upgrade() -> None:
    for comp in _COMPONENTS:
        op.execute(f"""
        INSERT INTO component_metadata (
            component_metadata_id,
            component_code,
            country_code,
            version,
            component_class,
            calculation_method,
            execution_priority,
            effective_from,
            is_active,
            metadata_json
        ) VALUES (
            gen_random_uuid(),
            '{comp["component_code"]}',
            'NG',
            1,
            '{comp["component_class"]}',
            '{comp["calculation_method"]}',
            {comp["execution_priority"]},
            '2026-01-01',
            TRUE,
            '{comp["metadata_json"]}'::jsonb
        )
        ON CONFLICT (component_code, country_code, version) DO NOTHING;
        """)


def downgrade() -> None:
    codes = ", ".join(f"'{c['component_code']}'" for c in _COMPONENTS)
    op.execute(f"""
    DELETE FROM component_metadata
    WHERE component_code IN ({codes})
      AND country_code   = 'NG'
      AND version        = 1;
    """)
