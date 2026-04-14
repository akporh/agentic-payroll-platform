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


def get_legacy_executor_stats() -> dict:
    """Return aggregate stats on legacy executor fallback usage.

    Returns:
        {
          "total_runs":          int,   # all payroll runs with at least one trace step
          "runs_with_legacy":    int,   # runs where legacy fallback fired at least once
          "pct_runs_affected":   float, # runs_with_legacy / total_runs * 100 (0 if no runs)
          "total_legacy_events": int,   # total employee-level fallback events across all runs
          "by_run": [                   # per-run breakdown (only runs with legacy events)
            {"run_id": str, "legacy_count": int}
          ]
        }
    """
    db = SessionLocal()
    try:
        agg = db.execute(
            text("""
                SELECT
                    COUNT(DISTINCT run_id)                                          AS total_runs,
                    COUNT(DISTINCT CASE WHEN step_name = 'legacy_executor_fallback'
                                        THEN run_id END)                           AS runs_with_legacy,
                    COUNT(CASE WHEN step_name = 'legacy_executor_fallback' THEN 1 END)
                                                                                   AS total_legacy_events
                FROM execution_trace
            """),
        ).fetchone()

        total_runs       = agg[0] or 0
        runs_with_legacy = agg[1] or 0
        total_legacy_events = agg[2] or 0
        pct = round(100.0 * runs_with_legacy / total_runs, 1) if total_runs else 0.0

        by_run_rows = db.execute(
            text("""
                SELECT run_id, COUNT(*) AS legacy_count
                FROM   execution_trace
                WHERE  step_name = 'legacy_executor_fallback'
                GROUP  BY run_id
                ORDER  BY legacy_count DESC
            """),
        ).fetchall()

        return {
            "total_runs":          total_runs,
            "runs_with_legacy":    runs_with_legacy,
            "pct_runs_affected":   pct,
            "total_legacy_events": total_legacy_events,
            "by_run": [
                {"run_id": str(r[0]), "legacy_count": r[1]}
                for r in by_run_rows
            ],
        }
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
