"""
Payroll Retry Service.

Retries only the FAILED employees from a PARTIAL payroll run.
Successful employees are never touched.

Retry flow (per employee)
--------------------------
1. Load the employee's current salary components from the DB.
2. Attempt payroll calculation (pure, no side-effects).
3. DELETE the old FAILED row  ← only after calculation completes (or fails).
4. INSERT the new result row (SUCCESS or FAILED).

The DELETE happens AFTER the calculation attempt — not before.  This means
the old row stays alive until we are certain of the replacement, so a crash
between step 2 and step 4 leaves the data in a consistent state (old FAILED
row is still there, not deleted).

Why DELETE + INSERT rather than UPDATE
---------------------------------------
trg_snapshot_immutable (migration fe0bad282b7d) fires BEFORE UPDATE OF
calculations_snapshot_json when the value changes.  FAILED rows store {},
a successful retry writes real values — so any UPDATE that touches that
column is rejected.  INSERT on a fresh row is not subject to this trigger.

The unique index uq_payroll_result_employee_run (migration 6f5b05ff4690)
enforces one result per (payroll_run_id, employee_id), so the DELETE must
precede the INSERT.

DELETE guard (status = 'FAILED')
---------------------------------
The DELETE includes AND status = 'FAILED'.  This prevents accidental
removal of a SUCCESS row in the (unlikely) event of a race between two
concurrent retry calls.  The FOR UPDATE lock on payroll_run makes such
races impossible under normal conditions, but the guard is a safety net.

Run status recomputation
------------------------
After all employees are processed, the new run status is derived by
counting ALL remaining FAILED rows for the run — not from local counters.
This is correct even if the DB already had partially inconsistent state
before the retry.

  remaining_failed == 0  →  CALCULATED
  remaining_failed  > 0  →  PARTIAL

The DB state machine trigger (migration 9901bc4ed0c5) only enforces
DRAFT, PROCESSING, COMPLETED, and PAID transitions.  PARTIAL → CALCULATED
falls through to RETURN NEW and is therefore allowed.

Idempotency
-----------
If no FAILED rows exist the function returns immediately with retried=0
without touching any data.

Blocked states
--------------
PAID runs are rejected before any work begins.  The DB triggers would also
reject any writes, but the early ValueError is cleaner.
"""

import json

from psycopg2.extras import Json
from sqlalchemy import text

from backend.domain.payroll.executor import execute_single_employee_payroll
from backend.infra.db.session import SessionLocal


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sanitize(obj: dict) -> dict:
    """Coerce Decimal / UUID / date values to JSON-safe types."""
    return json.loads(json.dumps(obj, default=str))


def _insert_result(
    db,
    *,
    payroll_run_id: str,
    employee_id: str,
    status: str,
    payroll_output: dict | None,
    error_message: str | None,
) -> None:
    """Insert a single payroll_result row."""

    if status == "SUCCESS" and payroll_output is not None:
        pr            = payroll_output["payroll_result"]
        gross_out     = _sanitize(pr["gross_components_jsonb"])
        ded_out       = _sanitize(pr["deductions_jsonb"])
        snap_out      = _sanitize(pr["calculations_snapshot_json"])
        net_pay       = pr["net_pay"]
        trace_raw     = pr.get("component_trace_jsonb")
        trace_out     = _sanitize(trace_raw) if trace_raw else None
    else:
        gross_out     = {}
        ded_out       = {}
        snap_out      = {}
        net_pay       = 0
        trace_out     = None

    db.execute(
        text("""
            INSERT INTO payroll_result (
                payroll_result_id,
                payroll_run_id,
                employee_id,
                gross_components_jsonb,
                deductions_jsonb,
                net_pay,
                calculations_snapshot_json,
                component_trace_jsonb,
                status,
                error_message
            )
            VALUES (
                gen_random_uuid(),
                :run_id,
                :eid,
                :gross,
                :deductions,
                :net_pay,
                :snapshot,
                :trace,
                :status,
                :error
            )
        """),
        {
            "run_id":     payroll_run_id,
            "eid":        employee_id,
            "gross":      Json(gross_out),
            "deductions": Json(ded_out),
            "net_pay":    net_pay,
            "snapshot":   Json(snap_out),
            "trace":      Json(trace_out) if trace_out is not None else None,
            "status":     status,
            "error":      error_message,
        },
    )


def _delete_failed_row(db, *, payroll_run_id: str, employee_id: str) -> None:
    """Delete the FAILED result for one employee.

    The AND status = 'FAILED' guard ensures this never removes a SUCCESS row
    even if called in an unexpected order.
    """
    db.execute(
        text("""
            DELETE FROM payroll_result
            WHERE payroll_run_id = :run_id
              AND employee_id    = :eid
              AND status         = 'FAILED'
        """),
        {"run_id": payroll_run_id, "eid": employee_id},
    )


# ---------------------------------------------------------------------------
# FULL_RUN retry helper
# ---------------------------------------------------------------------------

def _retry_full_run(db, payroll_run_id: str, workspace_id: str) -> dict:
    """Delete all existing payroll_result rows for the run and re-calculate
    every active employee in the workspace from scratch.

    Called inside the same transaction and DB session as the caller.
    """

    # 1. Load shared inputs (same pattern as the original run)
    stat_row = db.execute(
        text("SELECT statutory_rule_id, version FROM statutory_rule ORDER BY version DESC LIMIT 1")
    ).fetchone()

    if stat_row is None:
        raise ValueError("No statutory rule found")

    statutory_rule_id = str(stat_row[0])
    statutory_version = stat_row[1]

    tax_rows = db.execute(
        text("""
            SELECT lower_limit, upper_limit, rate
            FROM   tax_band
            WHERE  statutory_rule_id = :sr_id
            ORDER  BY lower_limit
        """),
        {"sr_id": statutory_rule_id},
    ).fetchall()

    tax_bands = [{"lower_limit": r[0], "upper_limit": r[1], "rate": r[2]} for r in tax_rows]

    rule_rows = db.execute(
        text("SELECT rule_id FROM payroll_rule WHERE is_active = TRUE AND workspace_id = :wid"),
        {"wid": workspace_id},
    ).fetchall()

    payroll_rule_ids = [str(r[0]) for r in rule_rows]

    # 2. Load ALL active employees for the workspace with current salary data
    emp_rows = db.execute(
        text("""
            SELECT e.employee_id, sd.components_jsonb
            FROM   employee e
            JOIN   employee_contract ec ON e.employee_id = ec.employee_id
            JOIN   salary_definition sd ON ec.salary_definition_id = sd.salary_definition_id
            WHERE  e.workspace_id = :wid
              AND  e.status       = 'ACTIVE'
              AND  (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
        """),
        {"wid": workspace_id},
    ).fetchall()

    if not emp_rows:
        raise ValueError("No active employees found for FULL_RUN retry")

    # 3. Delete ALL existing results (both SUCCESS and FAILED)
    db.execute(
        text("DELETE FROM payroll_result WHERE payroll_run_id = :run_id"),
        {"run_id": payroll_run_id},
    )

    # 4. Re-calculate every employee using the DELETE + INSERT pattern
    success_count = 0
    still_failed  = 0

    for emp in emp_rows:
        employee_id = str(emp[0])
        components  = [
            {"code": k, "amount": v["amount"] if isinstance(v, dict) else v}
            for k, v in emp[1].items()
        ]

        try:
            calc_result = execute_single_employee_payroll(
                payroll_run_id    = payroll_run_id,
                employee_id       = employee_id,
                components        = components,
                tax_bands         = tax_bands,
                statutory_rule_id = statutory_rule_id,
                statutory_version = statutory_version,
                payroll_rule_ids  = payroll_rule_ids,
                performed_by      = "admin@internal",
            )
            calc_error = None
        except Exception as exc:
            calc_result = None
            calc_error  = str(exc)

        if calc_error is None:
            _insert_result(
                db,
                payroll_run_id = payroll_run_id,
                employee_id    = employee_id,
                status         = "SUCCESS",
                payroll_output = calc_result,
                error_message  = None,
            )
            success_count += 1
        else:
            _insert_result(
                db,
                payroll_run_id = payroll_run_id,
                employee_id    = employee_id,
                status         = "FAILED",
                payroll_output = None,
                error_message  = calc_error,
            )
            still_failed += 1

    # 5. Recompute run status from DB (authoritative)
    remaining_failed = db.execute(
        text("SELECT COUNT(*) FROM payroll_result WHERE payroll_run_id = :run_id AND status = 'FAILED'"),
        {"run_id": payroll_run_id},
    ).scalar()

    new_run_status = "CALCULATED" if remaining_failed == 0 else "PARTIAL"

    db.execute(
        text("UPDATE payroll_run SET status = :status WHERE payroll_run_id = :run_id"),
        {"run_id": payroll_run_id, "status": new_run_status},
    )

    db.commit()

    return {
        "payroll_run_id": payroll_run_id,
        "retried":        len(emp_rows),
        "success":        success_count,
        "still_failed":   still_failed,
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def retry_failed_payroll_employees(payroll_run_id: str) -> dict:
    """Retry all FAILED employees in a PARTIAL payroll run.

    Args:
        payroll_run_id: The run to retry.

    Returns:
        {
            "payroll_run_id": str,
            "retried":        int,   # employees attempted
            "success":        int,   # newly successful
            "still_failed":   int,   # still failing after retry
        }

    Raises:
        ValueError: Run not found, is PAID, or is not PARTIAL.
    """

    db = SessionLocal()

    try:
        # -------------------------------------------------------------------
        # Step 1 — Lock the run row for the life of this transaction.
        #
        # FOR UPDATE prevents a concurrent /retry or /run call from
        # modifying the same run while we process employees.
        # -------------------------------------------------------------------
        run_row = db.execute(
            text("""
                SELECT workspace_id, status, retry_strategy
                FROM   payroll_run
                WHERE  payroll_run_id = :run_id
                FOR UPDATE
            """),
            {"run_id": payroll_run_id},
        ).fetchone()

        if run_row is None:
            raise ValueError(f"Payroll run not found: {payroll_run_id}")

        workspace_id   = str(run_row[0])
        current_status = run_row[1]
        retry_strategy = run_row[2] or "PER_EMPLOYEE"

        if current_status == "PAID":
            raise ValueError("Cannot retry a PAID payroll run")

        # Explicit guard for approved/locked runs — these are intentionally
        # immutable by business rule, not just incidentally wrong status.
        if current_status in ("APPROVED", "LOCKED"):
            raise ValueError(
                f"Payroll run is {current_status} and cannot be modified. "
                f"Only PARTIAL runs are eligible for retry."
            )

        if current_status != "PARTIAL":
            raise ValueError(
                f"Only PARTIAL runs can be retried. "
                f"Current status: {current_status}"
            )

        # -------------------------------------------------------------------
        # FULL_RUN branch — delete all results and re-run every employee.
        # -------------------------------------------------------------------
        if retry_strategy == "FULL_RUN":
            return _retry_full_run(db, payroll_run_id, workspace_id)

        # -------------------------------------------------------------------
        # Step 2 — Find FAILED employees (explicit status guard).
        # -------------------------------------------------------------------
        failed_rows = db.execute(
            text("""
                SELECT employee_id
                FROM   payroll_result
                WHERE  payroll_run_id = :run_id
                  AND  status         = 'FAILED'
            """),
            {"run_id": payroll_run_id},
        ).fetchall()

        # Idempotent: nothing to do
        if not failed_rows:
            db.commit()
            return {
                "payroll_run_id": payroll_run_id,
                "retried":        0,
                "success":        0,
                "still_failed":   0,
            }

        failed_employee_ids = [str(r[0]) for r in failed_rows]

        # -------------------------------------------------------------------
        # Step 3 — Load shared inputs (statutory rule, tax bands, rules).
        #          Same query as the original /payroll/run route.
        # -------------------------------------------------------------------
        stat_row = db.execute(
            text("""
                SELECT statutory_rule_id, version
                FROM   statutory_rule
                ORDER  BY version DESC
                LIMIT  1
            """)
        ).fetchone()

        if stat_row is None:
            raise ValueError("No statutory rule found")

        statutory_rule_id = str(stat_row[0])
        statutory_version = stat_row[1]

        tax_rows = db.execute(
            text("""
                SELECT lower_limit, upper_limit, rate
                FROM   tax_band
                WHERE  statutory_rule_id = :sr_id
                ORDER  BY lower_limit
            """),
            {"sr_id": statutory_rule_id},
        ).fetchall()

        tax_bands = [
            {"lower_limit": r[0], "upper_limit": r[1], "rate": r[2]}
            for r in tax_rows
        ]

        rule_rows = db.execute(
            text("""
                SELECT rule_id
                FROM   payroll_rule
                WHERE  is_active     = TRUE
                  AND  workspace_id  = :wid
            """),
            {"wid": workspace_id},
        ).fetchall()

        payroll_rule_ids = [str(r[0]) for r in rule_rows]

        # -------------------------------------------------------------------
        # Step 4 — Process each FAILED employee.
        #
        # Pattern (per employee):
        #   a) Attempt calculation  (pure, no DB writes)
        #   b) DELETE old FAILED row  ← after the attempt, never before
        #   c) INSERT new result (SUCCESS or FAILED)
        #
        # Keeping the old row alive until step (b) ensures the DB is never
        # left without a result row for this employee, even if the process
        # crashes between steps (a) and (c).
        # -------------------------------------------------------------------
        retried      = 0
        success_count = 0
        still_failed  = 0

        for employee_id in failed_employee_ids:

            # Load the employee's CURRENT salary components.
            # If the data was corrected since the original run (the normal
            # "fix then retry" workflow), the corrected values are picked up
            # here automatically.
            emp_row = db.execute(
                text("""
                    SELECT sd.components_jsonb
                    FROM   employee e
                    JOIN   employee_contract ec
                           ON e.employee_id = ec.employee_id
                    JOIN   salary_definition sd
                           ON ec.salary_definition_id = sd.salary_definition_id
                    WHERE  e.employee_id = :eid
                      AND  e.status      = 'ACTIVE'
                      AND  (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
                """),
                {"eid": employee_id},
            ).fetchone()

            # ----------------------------------------------------------------
            # a) Attempt calculation — pure, no DB side-effects.
            # ----------------------------------------------------------------
            if emp_row is None:
                # No active contract — the calculation cannot proceed.
                calc_result   = None
                calc_error    = "Employee has no active contract"
            else:
                components = [
                    {"code": k, "amount": v["amount"] if isinstance(v, dict) else v}
                    for k, v in emp_row[0].items()
                ]
                try:
                    calc_result = execute_single_employee_payroll(
                        payroll_run_id    = payroll_run_id,
                        employee_id       = employee_id,
                        components        = components,
                        tax_bands         = tax_bands,
                        statutory_rule_id = statutory_rule_id,
                        statutory_version = statutory_version,
                        payroll_rule_ids  = payroll_rule_ids,
                        performed_by      = "admin@internal",
                    )
                    calc_error = None
                except Exception as exc:
                    calc_result = None
                    calc_error  = str(exc)

            # ----------------------------------------------------------------
            # b) DELETE the old FAILED row — only after the attempt.
            #    status = 'FAILED' guard prevents touching SUCCESS rows.
            # ----------------------------------------------------------------
            _delete_failed_row(db, payroll_run_id=payroll_run_id, employee_id=employee_id)

            # ----------------------------------------------------------------
            # c) INSERT new result row.
            # ----------------------------------------------------------------
            if calc_error is None:
                _insert_result(
                    db,
                    payroll_run_id = payroll_run_id,
                    employee_id    = employee_id,
                    status         = "SUCCESS",
                    payroll_output = calc_result,
                    error_message  = None,
                )
                success_count += 1
            else:
                _insert_result(
                    db,
                    payroll_run_id = payroll_run_id,
                    employee_id    = employee_id,
                    status         = "FAILED",
                    payroll_output = None,
                    error_message  = calc_error,
                )
                still_failed += 1

            retried += 1

        # -------------------------------------------------------------------
        # Step 5 — Recompute run status from the DB (not from local counters).
        #
        # This is authoritative even if earlier state was inconsistent.
        # -------------------------------------------------------------------
        remaining_failed = db.execute(
            text("""
                SELECT COUNT(*)
                FROM   payroll_result
                WHERE  payroll_run_id = :run_id
                  AND  status         = 'FAILED'
            """),
            {"run_id": payroll_run_id},
        ).scalar()

        new_run_status = "CALCULATED" if remaining_failed == 0 else "PARTIAL"

        # trg_payroll_run_state_machine allows PARTIAL → CALCULATED
        # (only DRAFT / PROCESSING / COMPLETED / PAID transitions are enforced)
        db.execute(
            text("""
                UPDATE payroll_run
                SET    status = :status
                WHERE  payroll_run_id = :run_id
            """),
            {"run_id": payroll_run_id, "status": new_run_status},
        )

        db.commit()

        return {
            "payroll_run_id": payroll_run_id,
            "retried":        retried,
            "success":        success_count,
            "still_failed":   still_failed,
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
