"""convert all json columns to jsonb
Convert all Phase 1 JSON columns to JSONB
Ensures full operator + indexing support across payroll engine.

Revision ID: c4bdcbd77c48
Revises: e178ad859b44
Create Date: 2026-02-19 06:27:23.690831
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4bdcbd77c48'
down_revision: Union[str, Sequence[str], None] ='e178ad859b44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    conversions = [

        # AUDIT LOG
        ("audit_log", "old_value_jsonb"),
        ("audit_log", "new_value_jsonb"),

        # EMPLOYEE (encrypted payload structure)
        ("employee", "personal_details_encrypted"),

        # EVENT STORE
        ("event_store", "event_payload"),

        # PAYROLL RESULTS
        ("payroll_result", "gross_components_jsonb"),
        ("payroll_result", "deductions_jsonb"),
        ("payroll_result", "calculations_snapshot_json"),

        # PAYROLL RULES
        ("payroll_rule", "rule_definition_json"),

        # PAYROLL RUN CONTEXT SNAPSHOT
        ("payroll_run", "rules_context_snapshot"),

        # SALARY TEMPLATES
        ("salary_definition", "components_jsonb"),

        # STATUTORY RULES
        ("statutory_rule", "rules_jsonb"),
    ]

    for table, column in conversions:
        op.execute(f"""
        ALTER TABLE {table}
        ALTER COLUMN {column}
        TYPE jsonb
        USING {column}::jsonb;
        """)


def downgrade():
    # MVP downgrade not required
    pass

