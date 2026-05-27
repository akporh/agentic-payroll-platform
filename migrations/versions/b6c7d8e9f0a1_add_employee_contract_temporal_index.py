"""Add temporal index on employee_contract(employee_id, start_date).

end_date pre-exists from migration 7685c65f5d2; this migration adds a
performance index on (employee_id, start_date) to support the LATERAL JOIN
queries introduced in Sprint 17 that pick the most-recent contract per
employee.

Revision ID: b6c7d8e9f0a1
Revises: e4f5a6b7c8d9
"""

from alembic import op

revision: str = "b6c7d8e9f0a1"
down_revision: str = "e4f5a6b7c8d9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_employee_contract_employee_date
            ON employee_contract (employee_id, start_date)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_employee_contract_employee_date")
