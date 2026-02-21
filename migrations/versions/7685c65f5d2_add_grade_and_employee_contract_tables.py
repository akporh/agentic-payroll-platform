"""add grade and employee_contract tables

Revision ID: 7685c65f5d2
Revises: 5aa34350e00f
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "7685c65f5d2"
down_revision = "5aa34350e00f"
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa


def upgrade() -> None:

    # -------------------------
    # GRADE
    # -------------------------
    op.create_table(
        "grade",
        sa.Column("grade_id", sa.UUID(), primary_key=True),
        sa.Column("workspace_id", sa.UUID(), sa.ForeignKey("workspace.workspace_id"), nullable=False),
        sa.Column("grade_code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
    )

    # -------------------------
    # EMPLOYEE_CONTRACT
    # -------------------------
    op.create_table(
        "employee_contract",
        sa.Column("contract_id", sa.UUID(), primary_key=True),
        sa.Column("employee_id", sa.UUID(), sa.ForeignKey("employee.employee_id"), nullable=False),
        sa.Column("salary_definition_id", sa.UUID(), sa.ForeignKey("salary_definition.salary_definition_id"), nullable=False),
        sa.Column("grade_id", sa.UUID(), sa.ForeignKey("grade.grade_id"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("change_reason", sa.String(length=255), nullable=True),
    )

