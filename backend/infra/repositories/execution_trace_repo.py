"""
Execution Trace Repository.

Persists and retrieves structured step-level traces for payroll runs.
"""

from sqlalchemy import text
from backend.infra.db.session import SessionLocal


def save_trace_step(
    *,
    run_id: str,
    step_name: str,
    status: str,
    duration_ms: int | None,
    error_message: str | None = None,
) -> None:
    """Insert one execution_trace row.  Silently swallows all errors so
    that a trace write failure never interrupts the payroll run."""
    db = SessionLocal()
    try:
        db.execute(
            text("""
                INSERT INTO execution_trace
                    (run_id, step_name, status, duration_ms, error_message)
                VALUES
                    (:run_id, :step_name, :status, :duration_ms, :error_message)
            """),
            {
                "run_id":        run_id,
                "step_name":     step_name,
                "status":        status,
                "duration_ms":   duration_ms,
                "error_message": error_message,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def get_trace_steps(run_id: str) -> list[dict]:
    """Return all trace steps for a run, ordered by creation time."""
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT step_name, status, duration_ms, error_message, created_at
                FROM   execution_trace
                WHERE  run_id = :run_id
                ORDER  BY created_at ASC
            """),
            {"run_id": run_id},
        ).fetchall()

        return [
            {
                "step_name":     r[0],
                "status":        r[1],
                "duration_ms":   r[2],
                "error_message": r[3],
                "created_at":    r[4].isoformat() if r[4] else None,
            }
            for r in rows
        ]
    finally:
        db.close()
