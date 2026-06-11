"""
Payroll Input Repository.

Provides link_inputs_to_run() and load_inputs_for_run() for claiming
unclaimed payroll_input rows at run time and loading them into the
calculation chain.

Uses its own SessionLocal() per call — the route's session is already
closed before payroll_run_id is generated.
"""

from datetime import date

from sqlalchemy import text
from backend.infra.db.session import SessionLocal


def link_inputs_to_run(
    workspace_id:   str,
    payroll_run_id: str,
    period_start:   date | None = None,
    period_end:     date | None = None,
) -> int:
    """Claim unclaimed payroll_input rows for a workspace, optionally scoped to a period.

    reference_date records when the earning/deduction occurred, not which period
    it belongs to.  Classification by period window:
      - reference_date IS NULL              → period-agnostic, always claimed
      - reference_date <= period_end        → CURRENT or LATE, always claimed
      - reference_date > period_end         → FUTURE, never claimed

    When period_start/period_end are absent: claims ALL unclaimed rows for the
    workspace (v1 behaviour — backward compatible).

    Args:
        workspace_id:   The workspace whose unclaimed inputs to claim.
        payroll_run_id: The run to link the inputs to.
        period_start:   Optional start of the pay period (inclusive).
        period_end:     Optional end of the pay period (inclusive).

    Returns:
        Number of rows updated (claimed).
    """
    db = SessionLocal()
    try:
        if period_start is not None and period_end is not None:
            result = db.execute(
                text("""
                    UPDATE payroll_input
                    SET payroll_run_id = :run_id
                    WHERE workspace_id   = :wid
                      AND payroll_run_id IS NULL
                      AND (
                            reference_date IS NULL    -- period-agnostic
                         OR reference_date <= :pe     -- CURRENT or LATE (never FUTURE)
                      )
                """),
                {
                    "run_id": payroll_run_id,
                    "wid":    workspace_id,
                    "ps":     period_start,
                    "pe":     period_end,
                },
            )
        else:
            # v1 fallback: claim all unclaimed rows regardless of reference_date
            result = db.execute(
                text("""
                    UPDATE payroll_input
                    SET payroll_run_id = :run_id
                    WHERE workspace_id   = :wid
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
        Nested dict: {employee_id_str: {input_code: {quantity, category, reference_date}}}
    """
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT employee_id, input_code, input_category, quantity, reference_date, source
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
            if code not in inputs_by_employee[emp_id]:
                inputs_by_employee[emp_id][code] = []
            inputs_by_employee[emp_id][code].append({
                "quantity":       float(row[3]) if row[3] is not None else None,
                "category":       row[2],
                "reference_date": row[4],
                "source":         row[5] or "MANUAL",
            })
        return inputs_by_employee
    finally:
        db.close()


def load_unclaimed_inputs_by_employee(
    workspace_id:  str,
    period_start:  date | None = None,
    period_end:    date | None = None,
) -> dict:
    """Load unclaimed payroll_input rows for a workspace, keyed by employee_id.

    Does NOT claim (link) the inputs — no DB writes.  Used to populate
    employee inputs before the payroll_run row exists in the database.

    reference_date records when the earning/deduction occurred.  Classification:
      - reference_date IS NULL    → period-agnostic, always included
      - reference_date <= pe      → CURRENT or LATE, always included
      - reference_date > pe       → FUTURE, excluded
    When period_start/period_end are absent, all unclaimed rows are returned
    (v1 behaviour).

    Returns:
        Nested dict: {employee_id_str: {input_code: {quantity, category, reference_date}}}
        reference_date is a datetime.date or None (period-agnostic inputs).
    """
    db = SessionLocal()
    try:
        if period_start is not None and period_end is not None:
            rows = db.execute(
                text("""
                    SELECT employee_id, input_code, input_category, quantity, reference_date
                    FROM payroll_input
                    WHERE workspace_id   = :wid
                      AND payroll_run_id IS NULL
                      AND (
                            reference_date IS NULL    -- period-agnostic
                         OR reference_date <= :pe     -- CURRENT or LATE (never FUTURE)
                      )
                    ORDER BY employee_id, input_code
                """),
                {"wid": workspace_id, "ps": period_start, "pe": period_end},
            ).fetchall()
        else:
            rows = db.execute(
                text("""
                    SELECT employee_id, input_code, input_category, quantity, reference_date
                    FROM payroll_input
                    WHERE workspace_id = :wid AND payroll_run_id IS NULL
                    ORDER BY employee_id, input_code
                """),
                {"wid": workspace_id},
            ).fetchall()

        inputs_by_employee: dict = {}
        for row in rows:
            emp_id = str(row[0])
            code = row[1]
            if emp_id not in inputs_by_employee:
                inputs_by_employee[emp_id] = {}
            if code not in inputs_by_employee[emp_id]:
                inputs_by_employee[emp_id][code] = []
            inputs_by_employee[emp_id][code].append({
                "quantity":       float(row[3]) if row[3] is not None else None,
                "category":       row[2],
                "reference_date": row[4],
            })
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
                       pi.input_code, pi.input_category, pi.quantity,
                       pi.source, pi.created_at, pi.reference_date
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
                "source":           r[7] or "MANUAL",
                "created_at":       str(r[8]) if r[8] else None,
                "reference_date":   str(r[9]) if r[9] else None,
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
    reference_date: date | None = None,
) -> dict:
    """Insert an unclaimed payroll_input row. Returns the new ID."""
    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                INSERT INTO payroll_input (
                    payroll_input_id, workspace_id, employee_id,
                    input_code, input_category, quantity, source, reference_date
                ) VALUES (
                    gen_random_uuid(), :wid, :emp_id,
                    :code, :category, :qty, 'MANUAL', :reference_date
                )
                RETURNING payroll_input_id
            """),
            {
                "wid":            workspace_id,
                "emp_id":         employee_id,
                "code":           input_code,
                "category":       input_category,
                "qty":            quantity,
                "reference_date": reference_date,
            },
        ).fetchone()
        db.commit()
        return {"payroll_input_id": str(row[0])}
    finally:
        db.close()


def update_input(
    workspace_id: str,
    payroll_input_id: str,
    quantity,
    reference_date: date | None,
) -> bool:
    """Update quantity and reference_date on an unclaimed payroll_input row.

    Returns True if the row was found and updated, False if not found or
    already claimed by a run (payroll_run_id IS NOT NULL).
    """
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                UPDATE payroll_input
                   SET quantity       = :qty,
                       reference_date = :reference_date
                 WHERE payroll_input_id = :input_id
                   AND workspace_id    = :wid
                   AND payroll_run_id  IS NULL
            """),
            {
                "qty":            quantity,
                "reference_date": reference_date,
                "input_id":       payroll_input_id,
                "wid":            workspace_id,
            },
        )
        db.commit()
        return result.rowcount > 0
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


def delete_unclaimed_timesheet_inputs(
    workspace_id: str,
    employee_id: str,
    period_start: date,
    period_end: date,
) -> int:
    """Delete unclaimed TIMESHEET-source rows for an employee/period before re-derivation.

    MANUAL_OT and INPUT_FILE rows for the same employee/period are untouched.
    Returns number of rows deleted.
    """
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                DELETE FROM payroll_input
                WHERE workspace_id    = :wid
                  AND employee_id     = :emp_id
                  AND source          = 'TIMESHEET'
                  AND payroll_run_id  IS NULL
                  AND (
                        reference_date IS NULL
                     OR (reference_date >= :ps AND reference_date <= :pe)
                  )
            """),
            {"wid": workspace_id, "emp_id": employee_id, "ps": period_start, "pe": period_end},
        )
        db.commit()
        return result.rowcount
    finally:
        db.close()


def batch_create_timesheet_inputs(
    workspace_id: str,
    rows: list[dict],
    db=None,
) -> None:
    """Batch-insert TIMESHEET-source payroll_input rows inside the caller's transaction.

    Each dict in rows must have: employee_id, input_code, input_category, quantity,
    reference_date (may be None), rate_code (optional — stored as input_code if provided).

    If db is provided the caller owns the transaction and this function does NOT commit.
    If db is None a new session is opened and committed here.
    """
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        for row in rows:
            db.execute(
                text("""
                    INSERT INTO payroll_input (
                        payroll_input_id, workspace_id, employee_id,
                        input_code, input_category, quantity, source, reference_date
                    ) VALUES (
                        gen_random_uuid(), :wid, :emp_id,
                        :code, :category, :qty, 'TIMESHEET', :reference_date
                    )
                """),
                {
                    "wid":            workspace_id,
                    "emp_id":         row["employee_id"],
                    "code":           row["input_code"],
                    "category":       row["input_category"],
                    "qty":            row["quantity"],
                    "reference_date": row.get("reference_date"),
                },
            )
        if own_session:
            db.commit()
    finally:
        if own_session:
            db.close()
