"""Seed NG statutory components: NHF_CONTRIBUTION, HEALTH_INSURANCE_EMPLOYEE,
DEVELOPMENT_LEVY, LIFE_INSURANCE

Revision ID: c1d2e3f4a5b6
Revises: 1f644216db63
Create Date: 2026-03-19
"""
import uuid
from alembic import op
from sqlalchemy.dialects.postgresql import insert
import sqlalchemy as sa

revision = 'c1d2e3f4a5b6'
down_revision = '3b4c5d6e7f8a'
branch_labels = None
depends_on = None

_COMPONENTS = [
    {
        "component_code":     "NHF_CONTRIBUTION",
        "country_code":       "NG",
        "version":            1,
        "component_class":    "statutory_deduction",
        "calculation_method": "nhf_rule",
        "execution_priority": 410,
        "effective_from":     "2026-01-01",
        "is_active":          True,
        "metadata_json": {
            "financial_role": {
                "category":      "deduction",
                "affects_gross": False,
                "net_effect":    "decrease",
            },
            "legal_role": {
                "is_statutory":          True,
                "compliance_category":   "national_housing_fund",
                "governing_act":         "National Housing Fund Act",
                "default_employee_rate": 0.025,
            },
            "engine_behavior": {
                "derived_node": True,
                "base":         "BASIC",
            },
        },
    },
    {
        "component_code":     "HEALTH_INSURANCE_EMPLOYEE",
        "country_code":       "NG",
        "version":            1,
        "component_class":    "statutory_deduction",
        "calculation_method": "health_insurance_flat",
        "execution_priority": 420,
        "effective_from":     "2026-01-01",
        "is_active":          True,
        "metadata_json": {
            "financial_role": {
                "category":      "deduction",
                "affects_gross": False,
                "net_effect":    "decrease",
            },
            "legal_role": {
                "is_statutory":        False,
                "compliance_category": "health_insurance_employee",
                "note":                "HMO flat amount — override per workspace via client_component_metadata",
            },
            "engine_behavior": {
                "derived_node":     True,
                "amount_source":    "context.health_insurance_employee_amount",
                "workspace_override_key": "employee_monthly_amount",
            },
        },
    },
    {
        "component_code":     "DEVELOPMENT_LEVY",
        "country_code":       "NG",
        "version":            1,
        "component_class":    "statutory_deduction",
        "calculation_method": "development_levy_flat",
        "execution_priority": 430,
        "effective_from":     "2026-01-01",
        "is_active":          True,
        "metadata_json": {
            "financial_role": {
                "category":      "deduction",
                "affects_gross": False,
                "net_effect":    "decrease",
            },
            "legal_role": {
                "is_statutory":        True,
                "compliance_category": "development_levy",
                "note":                "Flat monthly state levy — configure per workspace via client_component_metadata",
            },
            "engine_behavior": {
                "derived_node":     True,
                "amount_source":    "context.development_levy_amount",
                "workspace_override_key": "monthly_amount",
            },
        },
    },
    {
        "component_code":     "LIFE_INSURANCE",
        "country_code":       "NG",
        "version":            1,
        "component_class":    "employer_cost",
        "calculation_method": "life_insurance_rule",
        "execution_priority": 440,
        "effective_from":     "2026-01-01",
        "is_active":          True,
        "metadata_json": {
            "financial_role": {
                "category":      "employer_cost",
                "affects_gross": False,
                "net_effect":    "none",
            },
            "legal_role": {
                "is_statutory":        True,
                "compliance_category": "group_life_insurance",
                "governing_act":       "Pension Reform Act 2014 s.9(3)",
                "note":                "Employer-only cost — not deducted from employee net pay",
            },
            "engine_behavior": {
                "derived_node": True,
                "base":         "GROSS_PAY",
            },
        },
    },
]


def upgrade():
    conn = op.get_bind()
    for comp in _COMPONENTS:
        conn.execute(
            sa.text("""
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
                    :country_code,
                    :version,
                    CAST(:metadata_json AS jsonb),
                    :effective_from,
                    :is_active,
                    :component_class,
                    :calculation_method,
                    :execution_priority
                )
                ON CONFLICT (component_code, country_code, version) DO NOTHING
            """),
            {
                "id":                 str(uuid.uuid4()),
                "component_code":     comp["component_code"],
                "country_code":       comp["country_code"],
                "version":            comp["version"],
                "metadata_json":      __import__("json").dumps(comp["metadata_json"]),
                "effective_from":     comp["effective_from"],
                "is_active":          comp["is_active"],
                "component_class":    comp["component_class"],
                "calculation_method": comp["calculation_method"],
                "execution_priority": comp["execution_priority"],
            },
        )


def downgrade():
    conn = op.get_bind()
    codes = [c["component_code"] for c in _COMPONENTS]
    conn.execute(
        sa.text("""
            DELETE FROM component_metadata
            WHERE component_code = ANY(:codes)
              AND country_code   = 'NG'
              AND version        = 1
        """),
        {"codes": codes},
    )
