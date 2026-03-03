"""add_component_metadata_designation_paycycle_workspace_status

Revision ID: 695bcbcc42f3
Revises: 423da33ffbd0
Create Date: 2026-03-03 03:24:33.018248

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = '695bcbcc42f3'
down_revision: Union[str, Sequence[str], None] = '423da33ffbd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    # ---------------------------------------------------
    # 1️⃣ Add workspace.status
    # ---------------------------------------------------
    op.add_column(
        "workspace",
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default="DRAFT"
        )
    )

    # ---------------------------------------------------
    # 2️⃣ Add tax_method to statutory_rule
    # ---------------------------------------------------
    op.add_column(
        "statutory_rule",
        sa.Column(
            "tax_method",
            sa.String(length=30),
            nullable=False,
            server_default="CUMULATIVE"
        )
    )

    # ---------------------------------------------------
    # 3️⃣ Create component_metadata (Platform Level)
    # ---------------------------------------------------
    op.create_table(
        "component_metadata",
        sa.Column("component_metadata_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("country_code", sa.String(10), nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("rules_jsonb", postgresql.JSONB, nullable=False),
        sa.Column("effective_from", sa.Date, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now())
    )

    op.create_index(
        "uq_component_metadata_country_version",
        "component_metadata",
        ["country_code", "version"],
        unique=True
    )

    # ---------------------------------------------------
    # 4️⃣ Create designation table (Workspace Level)
    # ---------------------------------------------------
    op.create_table(
        "designation",
        sa.Column("designation_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("designation_code", sa.String(100), nullable=False),
        sa.Column("description", sa.String(255)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now())
    )

    op.create_foreign_key(
        "fk_designation_workspace",
        "designation",
        "workspace",
        ["workspace_id"],
        ["workspace_id"]
    )

    op.create_index(
        "uq_designation_code_per_workspace",
        "designation",
        ["workspace_id", "designation_code"],
        unique=True
    )

    # ---------------------------------------------------
    # 5️⃣ Add designation_id to employee_contract
    # ---------------------------------------------------
    op.add_column(
        "employee_contract",
        sa.Column("designation_id", postgresql.UUID(as_uuid=True), nullable=True)
    )

    op.create_foreign_key(
        "fk_employee_contract_designation",
        "employee_contract",
        "designation",
        ["designation_id"],
        ["designation_id"]
    )

    # ---------------------------------------------------
    # 6️⃣ Create pay_cycle (Intent Layer)
    # ---------------------------------------------------
    op.create_table(
        "pay_cycle",
        sa.Column("pay_cycle_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("frequency", sa.String(20), nullable=False),
        sa.Column("run_day", sa.Integer, nullable=False),
        sa.Column("cutoff_day", sa.Integer, nullable=False),
        sa.Column("payment_day", sa.Integer, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now())
    )

    op.create_foreign_key(
        "fk_pay_cycle_workspace",
        "pay_cycle",
        "workspace",
        ["workspace_id"],
        ["workspace_id"]
    )

    op.create_index(
        "uq_pay_cycle_workspace",
        "pay_cycle",
        ["workspace_id"],
        unique=True
    )


def downgrade():

    op.drop_table("pay_cycle")

    op.drop_constraint("fk_employee_contract_designation", "employee_contract", type_="foreignkey")
    op.drop_column("employee_contract", "designation_id")

    op.drop_table("designation")

    op.drop_index("uq_component_metadata_country_version", table_name="component_metadata")
    op.drop_table("component_metadata")

    op.drop_column("statutory_rule", "tax_method")

    op.drop_column("workspace", "status")
