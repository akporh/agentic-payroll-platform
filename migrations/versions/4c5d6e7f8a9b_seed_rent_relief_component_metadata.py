"""seed RENT_RELIEF component metadata for NG

Adds RENT_RELIEF as a first-class sequential executor component at
priority 250 (between PENSION_EMPLOYEE and TAXABLE_INCOME).

component_class = 'statutory_relief' — deliberately not 'statutory_deduction'
so it is excluded from the net_formula deduction sum and deductions_jsonb.
It reduces taxable income (via TAXABLE_INCOME), not net pay directly.

The eligibility conditions in metadata_json gate execution on the presence
of a positive ANNUAL_RENT_PAID payroll_input row. Employees without one
are skipped silently (on_ineligible = 'skip').

Revision ID: 4c5d6e7f8a9b
Revises: 3b4c5d6e7f8a
Create Date: 2026-03-19
"""
import sqlalchemy as sa
from alembic import op

revision = '4c5d6e7f8a9b'
down_revision = '3b4c5d6e7f8a'
branch_labels = None
depends_on = None

_RENT_RELIEF_ID = 'a0000001-0000-0000-0000-000000000010'

_METADATA_JSON = """{
  "input_requirements": {
    "fields": [
      {
        "input_code":    "ANNUAL_RENT_PAID",
        "type":          "currency",
        "required":      true,
        "source":        "payroll_input",
        "label":         "Annual Rent Paid",
        "description":   "Employee declared annual residential rent payment"
      }
    ]
  },
  "eligibility": {
    "conditions": [
      { "type": "input_present", "input_code": "ANNUAL_RENT_PAID" },
      { "type": "input_value",   "input_code": "ANNUAL_RENT_PAID", "operator": "gt", "value": 0 }
    ],
    "logic": "ALL",
    "on_ineligible": "skip"
  },
  "calculation": {
    "method":      "rent_relief",
    "base":        { "source": "payroll_input", "input_code": "ANNUAL_RENT_PAID" },
    "rate_source": "statutory_rule.reliefs.rent_relief.rate",
    "cap_source":  "statutory_rule.reliefs.rent_relief.cap",
    "period":      "annual",
    "output":      "monthly"
  },
  "financial_role": {
    "category":               "statutory_relief",
    "net_effect":             "increase",
    "affects_gross":          false,
    "reduces_taxable_income": true
  },
  "legal_role": {
    "is_statutory":        true,
    "compliance_category": "tax_relief",
    "legislation":         "Nigeria Tax Act 2025"
  },
  "engine_behavior": {
    "derived_node":        true,
    "pass_to_paye_handler": true
  }
}"""


def upgrade():
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
            'RENT_RELIEF',
            'NG',
            1,
            :metadata_json,
            '2025-01-01',
            TRUE,
            'statutory_relief',
            'rent_relief',
            250
        )
        ON CONFLICT (component_code, country_code, version) DO UPDATE
            SET component_class    = EXCLUDED.component_class,
                calculation_method = EXCLUDED.calculation_method,
                execution_priority = EXCLUDED.execution_priority,
                metadata_json      = EXCLUDED.metadata_json
    """).bindparams(
        id=_RENT_RELIEF_ID,
        metadata_json=_METADATA_JSON,
    ))


def downgrade():
    op.execute(sa.text("""
        DELETE FROM component_metadata
        WHERE component_code = 'RENT_RELIEF'
          AND country_code   = 'NG'
          AND version        = 1
    """))
