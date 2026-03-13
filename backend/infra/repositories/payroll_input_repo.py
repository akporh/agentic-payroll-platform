"""
Payroll Input Repository.

Provides link_inputs_to_run() and load_inputs_for_run() for claiming
unclaimed payroll_input rows at run time and loading them into the
calculation chain.

Uses its own SessionLocal() per call — the route's session is already
closed before payroll_run_id is generated.
"""

from sqlalchemy import text
from backend.infra.db.session import SessionLocal


def link_inputs_to_run(workspace_id: str, payroll_run_id: str) -> int:
    """Claim all unclaimed payroll_input rows for a workspace.

    Sets payroll_run_id on every row where workspace_id matches and
    payroll_run_id IS NULL.

    Args:
        workspace_id: The workspace whose unclaimed inputs to claim.
        payroll_run_id: The run to link the inputs to.

    Returns:
        Number of rows updated (claimed).
    """
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                UPDATE payroll_input
                SET payroll_run_id = :run_id
                WHERE workspace_id = :wid
                  AND payroll_run_id IS NULL
            """),
            {"run_id": payroll_run_id, "wid": workspace_id},
        )
        db.commit()
        return result.rowcount
    finally:
        db.close()


def load_inputs_for_run(payroll_run_id: str) -> dict:
    """Load all inputs claimed by a payroll run, keyed by employee_id.

    Args:
        payroll_run_id: The run whose inputs to load.

    Returns:
        Nested dict: {employee_id_str: {input_code: {quantity, rate, amount, category}}}
    """
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT employee_id, input_code, input_category, quantity, rate, amount
                FROM payroll_input
                WHERE payroll_run_id = :run_id
                ORDER BY employee_id, input_code
            """),
            {"run_id": payroll_run_id},
        ).fetchall()

        inputs_by_employee: dict = {}
        for row in rows:
            emp_id = str(row[0])
            code = row[1]
            if emp_id not in inputs_by_employee:
                inputs_by_employee[emp_id] = {}
            inputs_by_employee[emp_id][code] = {
                "quantity": float(row[3]) if row[3] is not None else None,
                "rate":     float(row[4]) if row[4] is not None else None,
                "amount":   float(row[5]) if row[5] is not None else None,
                "category": row[2],
            }
        return inputs_by_employee
    finally:
        db.close()


def list_unclaimed_inputs(workspace_id: str) -> list[dict]:
    """Return all unclaimed payroll_input rows for a workspace."""
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT pi.payroll_input_id, pi.employee_id, e.full_name, e.employee_number,
                       pi.input_code, pi.input_category, pi.quantity, pi.rate, pi.amount,
                       pi.source, pi.created_at
                FROM payroll_input pi
                JOIN employee e ON e.employee_id = pi.employee_id
                WHERE pi.workspace_id = :wid AND pi.payroll_run_id IS NULL
                ORDER BY e.full_name, pi.input_code
            """),
            {"wid": workspace_id},
        ).fetchall()

        return [
            {
                "payroll_input_id": str(r[0]),
                "employee_id":      str(r[1]),
                "employee_name":    r[2] or "",
                "employee_number":  r[3] or "",
                "input_code":       r[4],
                "input_category":   r[5],
                "quantity":         float(r[6]) if r[6] is not None else None,
                "rate":             float(r[7]) if r[7] is not None else None,
                "amount":           float(r[8]) if r[8] is not None else None,
                "source":           r[9] or "MANUAL",
                "created_at":       str(r[10]) if r[10] else None,
            }
            for r in rows
        ]
    finally:
        db.close()


def create_input(
    workspace_id: str,
    employee_id: str,
    input_code: str,
    input_category: str,
    quantity,
    rate,
    amount,
) -> dict:
    """Insert an unclaimed payroll_input row. Returns the new ID."""
    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                INSERT INTO payroll_input (
                    payroll_input_id, workspace_id, employee_id,
                    input_code, input_category, quantity, rate, amount, source
                ) VALUES (
                    gen_random_uuid(), :wid, :emp_id,
                    :code, :category, :qty, :rate, :amount, 'MANUAL'
                )
                RETURNING payroll_input_id
            """),
            {
                "wid":      workspace_id,
                "emp_id":   employee_id,
                "code":     input_code,
                "category": input_category,
                "qty":      quantity,
                "rate":     rate,
                "amount":   amount,
            },
        ).fetchone()
        db.commit()
        return {"payroll_input_id": str(row[0])}
    finally:
        db.close()


def delete_input(workspace_id: str, payroll_input_id: str) -> bool:
    """Delete an unclaimed payroll_input row. Returns True if deleted."""
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                DELETE FROM payroll_input
                WHERE payroll_input_id = :input_id
                  AND workspace_id = :wid
                  AND payroll_run_id IS NULL
            """),
            {"input_id": payroll_input_id, "wid": workspace_id},
        )
        db.commit()
        return result.rowcount > 0
    finally:
        db.close()
