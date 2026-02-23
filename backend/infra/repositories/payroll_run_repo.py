"""
Payroll Run Repository.
"""

from sqlalchemy import text
from backend.infra.db.session import SessionLocal


def save_payroll_run(
    payroll_run_id: str,
    workspace_id: str,
    status: str,
):
    db = SessionLocal()

    db.execute(
        text("""
        INSERT INTO payroll_run (
            payroll_run_id,
            workspace_id,
            status
        )
        VALUES (
            :payroll_run_id,
            :workspace_id,
            :status
        )
        """),
        {
            "payroll_run_id": payroll_run_id,
            "workspace_id": workspace_id,
            "status": status,
        }
    )

    db.commit()
    db.close()
