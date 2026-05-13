"""
Timesheet Repository.

CRUD for timesheet_entry rows. All queries are workspace-scoped.
derivation_status transitions are write-once per derivation cycle —
re-upload resets to PENDING; derivation writes DERIVED or FAILED;
approval writes APPROVED.
"""

import json
from datetime import date
from decimal import Decimal

from sqlalchemy import text
from backend.infra.db.session import SessionLocal


def _decimal_serialiser(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serialisable")


def upsert_timesheet_entry(
    workspace_id: str,
    employee_id: str,
    period_start: date,
    period_end: date,
    grid_dict: dict,
) -> dict:
    """Insert or replace a timesheet entry for an employee/period.

    On conflict (same workspace/employee/period), the existing row is replaced:
    - attendance_grid_jsonb is overwritten
    - derivation_status resets to PENDING
    - derivation_error and policy_snapshot_jsonb are cleared
    Returns the entry dict with the assigned ID.
    """
    grid_json = json.dumps(grid_dict, default=_decimal_serialiser)
    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                INSERT INTO timesheet_entry
                    (timesheet_entry_id, workspace_id, employee_id,
                     period_start, period_end, attendance_grid_jsonb,
                     derivation_status, derivation_error,
                     policy_snapshot_jsonb, derivation_summary_jsonb)
                VALUES
                    (gen_random_uuid(), :wid, :emp_id,
                     :period_start, :period_end, CAST(:grid AS jsonb),
                     'PENDING', NULL, NULL, NULL)
                ON CONFLICT (workspace_id, employee_id, period_start) DO UPDATE
                SET
                    period_end               = EXCLUDED.period_end,
                    attendance_grid_jsonb    = EXCLUDED.attendance_grid_jsonb,
                    derivation_status        = 'PENDING',
                    derivation_error         = NULL,
                    policy_snapshot_jsonb    = NULL,
                    derivation_summary_jsonb = NULL,
                    updated_at               = now()
                RETURNING timesheet_entry_id, derivation_status
            """),
            {
                "wid":          workspace_id,
                "emp_id":       employee_id,
                "period_start": period_start,
                "period_end":   period_end,
                "grid":         grid_json,
            },
        ).fetchone()
        db.commit()
        return {
            "timesheet_entry_id": str(row[0]),
            "derivation_status":  row[1],
        }
    finally:
        db.close()


def get_entries_for_period(workspace_id: str, period_start: date) -> list[dict]:
    """Return all timesheet entries for a workspace/period, joined with employee info."""
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT
                    te.timesheet_entry_id, te.employee_id,
                    e.full_name, e.employee_number,
                    te.period_start, te.period_end,
                    te.derivation_status, te.derivation_error,
                    te.derivation_summary_jsonb, te.updated_at
                FROM timesheet_entry te
                JOIN employee e ON e.employee_id = te.employee_id
                WHERE te.workspace_id = :wid
                  AND te.period_start  = :period_start
                ORDER BY e.full_name
            """),
            {"wid": workspace_id, "period_start": period_start},
        ).fetchall()

        return [
            {
                "timesheet_entry_id":      str(r[0]),
                "employee_id":             str(r[1]),
                "employee_name":           r[2] or "",
                "employee_number":         r[3] or "",
                "period_start":            r[4].isoformat(),
                "period_end":              r[5].isoformat(),
                "derivation_status":       r[6],
                "derivation_error":        r[7],
                "derivation_summary":      r[8],
                "updated_at":              r[9].isoformat() if r[9] else None,
            }
            for r in rows
        ]
    finally:
        db.close()


def get_entry_with_grid(workspace_id: str, employee_id: str, period_start: date) -> dict | None:
    """Return a single entry including its attendance_grid_jsonb."""
    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                SELECT
                    timesheet_entry_id, employee_id, period_start, period_end,
                    attendance_grid_jsonb, derivation_status, derivation_error,
                    policy_snapshot_jsonb, derivation_summary_jsonb
                FROM timesheet_entry
                WHERE workspace_id = :wid
                  AND employee_id  = :emp_id
                  AND period_start = :period_start
            """),
            {"wid": workspace_id, "emp_id": employee_id, "period_start": period_start},
        ).fetchone()

        if row is None:
            return None

        return {
            "timesheet_entry_id":      str(row[0]),
            "employee_id":             str(row[1]),
            "period_start":            row[2].isoformat(),
            "period_end":              row[3].isoformat(),
            "attendance_grid_jsonb":   row[4],
            "derivation_status":       row[5],
            "derivation_error":        row[6],
            "policy_snapshot_jsonb":   row[7],
            "derivation_summary_jsonb": row[8],
        }
    finally:
        db.close()


def update_derivation_result(
    workspace_id: str,
    timesheet_entry_id: str,
    status: str,
    summary: dict | None = None,
    error: str | None = None,
    snapshot: dict | None = None,
    db=None,
) -> None:
    """Write derivation outcome back to a timesheet_entry row.

    If db is provided the caller owns the transaction; this function does NOT commit.
    """
    summary_json  = json.dumps(summary,  default=_decimal_serialiser) if summary  else None
    snapshot_json = json.dumps(snapshot, default=_decimal_serialiser) if snapshot else None

    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        db.execute(
            text("""
                UPDATE timesheet_entry
                SET
                    derivation_status        = CAST(:status AS derivation_status),
                    derivation_error         = :error,
                    derivation_summary_jsonb = CAST(:summary AS jsonb),
                    policy_snapshot_jsonb    = CAST(:snapshot AS jsonb),
                    updated_at               = now()
                WHERE timesheet_entry_id = :entry_id
                  AND workspace_id       = :wid
            """),
            {
                "wid":      workspace_id,
                "entry_id": timesheet_entry_id,
                "status":   status,
                "error":    error,
                "summary":  summary_json,
                "snapshot": snapshot_json,
            },
        )
        if own_session:
            db.commit()
    finally:
        if own_session:
            db.close()


def get_non_approved_employees(workspace_id: str, period_start: date) -> list[str]:
    """Return employee names/numbers for entries that are NOT APPROVED.

    Used by payroll_readiness_service to block run submission.
    """
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT e.full_name, e.employee_number, te.derivation_status
                FROM timesheet_entry te
                JOIN employee e ON e.employee_id = te.employee_id
                WHERE te.workspace_id      = :wid
                  AND te.period_start      = :period_start
                  AND te.derivation_status != 'APPROVED'
                ORDER BY e.full_name
            """),
            {"wid": workspace_id, "period_start": period_start},
        ).fetchall()

        return [
            f"{r[0] or r[1]} ({r[2]})"
            for r in rows
        ]
    finally:
        db.close()


def get_approved_entries_for_period(workspace_id: str, period_start: date) -> list[dict]:
    """Return APPROVED entries with their grids for the approval write step."""
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT
                    timesheet_entry_id, employee_id,
                    period_start, period_end,
                    derivation_summary_jsonb, policy_snapshot_jsonb
                FROM timesheet_entry
                WHERE workspace_id      = :wid
                  AND period_start      = :period_start
                  AND derivation_status = 'DERIVED'
                ORDER BY employee_id
            """),
            {"wid": workspace_id, "period_start": period_start},
        ).fetchall()

        return [
            {
                "timesheet_entry_id":      str(r[0]),
                "employee_id":             str(r[1]),
                "period_start":            r[2].isoformat(),
                "period_end":              r[3].isoformat(),
                "derivation_summary":      r[4],
                "policy_snapshot":         r[5],
            }
            for r in rows
        ]
    finally:
        db.close()


def set_entries_approved(workspace_id: str, period_start: date, db=None) -> int:
    """Set all DERIVED entries for a period to APPROVED. Returns count updated."""
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        result = db.execute(
            text("""
                UPDATE timesheet_entry
                SET derivation_status = 'APPROVED', updated_at = now()
                WHERE workspace_id      = :wid
                  AND period_start      = :period_start
                  AND derivation_status = 'DERIVED'
            """),
            {"wid": workspace_id, "period_start": period_start},
        )
        if own_session:
            db.commit()
        return result.rowcount
    finally:
        if own_session:
            db.close()
