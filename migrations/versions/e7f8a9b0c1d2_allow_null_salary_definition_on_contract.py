"""Allow NULL salary_definition_id on employee_contract

Employees can now be registered without a salary definition (not-enrolled state).
Enrollment (EMP-REG-2) sets salary_definition_id later via the enroll endpoint.

Revision ID: e7f8a9b0c1d2
Revises: b5c6d7e8f9a0
Create Date: 2026-06-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e7f8a9b0c1d2"
down_revision: Union[str, Sequence[str], None] = "b5c6d7e8f9a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "employee_contract",
        "salary_definition_id",
        existing_type=sa.dialects.postgresql.UUID(as_uuid=True),
        nullable=True,
    )


def downgrade() -> None:
    # Safety: refuse to restore NOT NULL if any NULLs exist (D-ENROLL-4)
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT COUNT(*) FROM employee_contract WHERE salary_definition_id IS NULL"
        )
    ).scalar()
    if result > 0:
        raise RuntimeError(
            f"Cannot downgrade: {result} employee_contract row(s) have NULL "
            "salary_definition_id. Enroll all employees before downgrading."
        )
    op.alter_column(
        "employee_contract",
        "salary_definition_id",
        existing_type=sa.dialects.postgresql.UUID(as_uuid=True),
        nullable=False,
    )
