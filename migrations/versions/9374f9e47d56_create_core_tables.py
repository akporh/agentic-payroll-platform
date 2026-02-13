"""create core tables

Revision ID: 9374f9e47d56
Revises:
Create Date: 2026-02-13

"""
from alembic import op
import sqlalchemy as sa

revision = "9374f9e47d56"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "account",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "workspace",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("account_id", sa.UUID(), sa.ForeignKey("account.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "employee",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("workspace_id", sa.UUID(), sa.ForeignKey("workspace.id"), nullable=False),

        sa.Column("employee_number", sa.String(length=50), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),

        sa.Column("status", sa.String(length=30), nullable=False, server_default="ACTIVE"),

        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_index(
        "ix_employee_workspace_employee_number",
        "employee",
        ["workspace_id", "employee_number"],
        unique=True,
    )

    op.create_table(
        "salary_component",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("workspace_id", sa.UUID(), sa.ForeignKey("workspace.id"), nullable=False),

        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),

        sa.Column("component_type", sa.String(length=30), nullable=False),  # EARNING/DEDUCTION
        sa.Column("taxable", sa.Boolean(), nullable=False, server_default=sa.true()),

        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_index(
        "ix_salary_component_workspace_code",
        "salary_component",
        ["workspace_id", "code"],
        unique=True,
    )

def downgrade() -> None:
    op.drop_table("workspace")
    op.drop_table("account")
    op.drop_index("ix_employee_workspace_employee_number", table_name="employee")
    op.drop_table("employee")
    op.drop_index("ix_salary_component_workspace_code", table_name="salary_component")
    op.drop_table("salary_component")

