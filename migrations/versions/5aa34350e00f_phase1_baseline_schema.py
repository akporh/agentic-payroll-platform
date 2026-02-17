"""phase1 baseline schema

Revision ID: 5aa34350e00f
Revises: 
Create Date: 2026-02-17 04:43:26.750437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5aa34350e00f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ---------- Core Tenancy ----------
    op.create_table(
        "account",
        sa.Column("account_id", sa.UUID(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "workspace",
        sa.Column("workspace_id", sa.UUID(), primary_key=True),
        sa.Column("account_id", sa.UUID(), sa.ForeignKey("account.account_id")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "employee",
        sa.Column("employee_id", sa.UUID(), primary_key=True),
        sa.Column("workspace_id", sa.UUID(), sa.ForeignKey("workspace.workspace_id")),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # ---------- Rules ----------
    op.create_table(
        "statutory_rule",
        sa.Column("statutory_rule_id", sa.UUID(), primary_key=True),
        sa.Column("state", sa.String(50), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("rules_jsonb", sa.JSON(), nullable=False),
    )

    op.create_table(
        "tax_band",
        sa.Column("tax_band_id", sa.UUID(), primary_key=True),
        sa.Column("statutory_rule_id", sa.UUID(),
                  sa.ForeignKey("statutory_rule.statutory_rule_id")),
        sa.Column("lower_limit", sa.Numeric(), nullable=False),
        sa.Column("upper_limit", sa.Numeric(), nullable=True),
        sa.Column("rate", sa.Numeric(), nullable=False),
    )

    op.create_table(
        "payroll_rule",
        sa.Column("payroll_rule_id", sa.UUID(), primary_key=True),
        sa.Column("workspace_id", sa.UUID(), sa.ForeignKey("workspace.workspace_id")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("rule_jsonb", sa.JSON(), nullable=False),
    )

    # ---------- Salary Definition ----------
    op.create_table(
        "salary_definition",
        sa.Column("salary_definition_id", sa.UUID(), primary_key=True),
        sa.Column("employee_id", sa.UUID(), sa.ForeignKey("employee.employee_id")),
        sa.Column("components_jsonb", sa.JSON(), nullable=False),
    )

    # ---------- Payroll Execution ----------
    op.create_table(
        "payroll_run",
        sa.Column("payroll_run_id", sa.UUID(), primary_key=True),
        sa.Column("workspace_id", sa.UUID(), sa.ForeignKey("workspace.workspace_id")),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("rules_context_snapshot", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "payroll_result",
        sa.Column("payroll_result_id", sa.UUID(), primary_key=True),
        sa.Column("payroll_run_id", sa.UUID(),
                  sa.ForeignKey("payroll_run.payroll_run_id")),
        sa.Column("employee_id", sa.UUID(), sa.ForeignKey("employee.employee_id")),
        sa.Column("gross_components_jsonb", sa.JSON(), nullable=False),
        sa.Column("deductions_jsonb", sa.JSON(), nullable=False),
        sa.Column("net_pay", sa.Numeric(), nullable=False),
        sa.Column("calculations_snapshot_json", sa.JSON(), nullable=False),
    )

    # ---------- Audit + Event Store ----------
    op.create_table(
        "audit_log",
        sa.Column("audit_log_id", sa.UUID(), primary_key=True),
        sa.Column("workspace_id", sa.UUID(), sa.ForeignKey("workspace.workspace_id")),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("old_value_jsonb", sa.JSON(), nullable=True),
        sa.Column("new_value_jsonb", sa.JSON(), nullable=True),
        sa.Column("performed_by", sa.String(), nullable=False),
        sa.Column("performed_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "event_store",
        sa.Column("event_id", sa.UUID(), primary_key=True),
        sa.Column("aggregate_type", sa.String(), nullable=False),
        sa.Column("aggregate_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("event_payload", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
