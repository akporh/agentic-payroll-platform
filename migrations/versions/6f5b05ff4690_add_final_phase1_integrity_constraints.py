"""add final phase1 integrity constraints

Revision ID: 6f5b05ff4690
Revises: cb7a1109fc48
Create Date: 2026-02-19 09:27:21.334564

Final Phase 1 Integrity Constraints

Locks core payroll correctness:

- One active contract per employee
- Unique employee_number per workspace
- Unique grade_code per workspace
- Unique salary_definition name per workspace
- Unique payroll_run per period per workspace
- Unique payroll_result per employee per run

These constraints enforce Phase 1 payroll truth guarantees.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f5b05ff4690'
down_revision: Union[str, Sequence[str], None] = 'cb7a1109fc48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():

    # =========================================================
    # 1. EMPLOYEE: employee_number must be unique per workspace
    # =========================================================
    op.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS uq_employee_number_per_workspace
    ON employee(workspace_id, employee_number);
    """)

    # =========================================================
    # 2. GRADE: grade_code must be unique per workspace
    # =========================================================
    op.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS uq_grade_code_per_workspace
    ON grade(workspace_id, grade_code);
    """)

    # =========================================================
    # 3. SALARY_DEFINITION: name must be unique per workspace
    # =========================================================
    op.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS uq_salary_definition_name_per_workspace
    ON salary_definition(workspace_id, name);
    """)

    # =========================================================
    # 4. EMPLOYEE_CONTRACT: only one active contract at a time
    # =========================================================
    op.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS uq_employee_active_contract
    ON employee_contract(employee_id)
    WHERE end_date IS NULL;
    """)

    # =========================================================
    # 5. PAYROLL_RUN: only one run per period per workspace
    # =========================================================
    op.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS uq_payroll_run_period
    ON payroll_run(workspace_id, period_start, period_end);
    """)

    # =========================================================
    # 6. PAYROLL_RESULT: only one payslip per employee per run
    # =========================================================
    op.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS uq_payroll_result_employee_run
    ON payroll_result(payroll_run_id, employee_id);
    """)


def downgrade():
    # Phase 1 MVP downgrade not required
    pass

