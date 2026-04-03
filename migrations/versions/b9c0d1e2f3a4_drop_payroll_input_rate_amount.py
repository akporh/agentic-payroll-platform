"""Drop unused rate and amount columns from payroll_input.

These columns were stored but never read by the payroll engine.
Rates for overtime / unit-multiplier rules come from
payroll_rule.rule_definition_json["rate"].
Absence deduction rates are derived from salary_definition.components_jsonb
divided by the period working/calendar days.
payroll_input.quantity remains as the event count (days absent, overtime units).

Revision ID: b9c0d1e2f3a4
Revises: a8b9c0d1e2f3
"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "b9c0d1e2f3a4"
down_revision: Union[str, Sequence[str], None] = "a8b9c0d1e2f3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("payroll_input", "rate")
    op.drop_column("payroll_input", "amount")


def downgrade() -> None:
    op.add_column("payroll_input", sa.Column("rate",   sa.Numeric(12, 2), nullable=True))
    op.add_column("payroll_input", sa.Column("amount", sa.Numeric(12, 2), nullable=True))
