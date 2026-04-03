"""add jsonb integrity constraints for payroll outputs and rules
JSONB Integrity Constraints (Phase 1)

Adds structural guarantees for:

- payroll_result JSONB outputs
- payroll_rule JSONB rule definitions

Goal:
Prevent invalid shapes (arrays/scalars) entering core payroll truth tables.

We intentionally do NOT constrain event_store or audit_log payloads.

Revision ID: ea05e71efbd7
Revises: c789a9f78a41
Create Date: 2026-02-19 07:52:31.922701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea05e71efbd7'
down_revision: Union[str, Sequence[str], None] = 'c789a9f78a41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    # =========================================================
    # PAYROLL_RESULT: Output JSONB must always be objects
    # =========================================================

    # Gross pay breakdown must be a JSON object
    op.execute("""
    ALTER TABLE payroll_result
    ADD CONSTRAINT chk_gross_components_is_object
    CHECK (jsonb_typeof(gross_components_jsonb::jsonb) = 'object');
    """)

    # Deductions breakdown must be a JSON object
    op.execute("""
    ALTER TABLE payroll_result
    ADD CONSTRAINT chk_deductions_is_object
    CHECK (jsonb_typeof(deductions_jsonb::jsonb) = 'object');
    """)

    # Calculation reasoning snapshot must be a JSON object
    op.execute("""
    ALTER TABLE payroll_result
    ADD CONSTRAINT chk_calculation_snapshot_is_object
    CHECK (jsonb_typeof(calculations_snapshot_json::jsonb) = 'object');
    """)

    # =========================================================
    # PAYROLL_RULE: Rule definition must always be an object
    # =========================================================

    op.execute("""
    ALTER TABLE payroll_rule
    ADD CONSTRAINT chk_rule_definition_is_object
    CHECK (jsonb_typeof(rule_definition_json::jsonb) = 'object');
    """)

    # =========================================================
    # Optional: Light sanity requirement (rule must include logic key)
    # Uncomment later once rules stabilize
    # =========================================================
    #
    # op.execute("""
    # ALTER TABLE payroll_rule
    # ADD CONSTRAINT chk_rule_definition_has_formula
    # CHECK (rule_definition_json ? 'formula');
    # """)


def downgrade():
    # MVP downgrade not required
    pass
