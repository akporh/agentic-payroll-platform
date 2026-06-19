import json
import logging
from decimal import Decimal

from psycopg2.extras import Json, execute_values

from backend.infra.db.session import SessionLocal, engine

_log = logging.getLogger(__name__)


# ── helpers ───────────────────────────────────────────────────────────────────

def _as_json(value):
    """Convert a value to a psycopg2 Json adapter for execute_values.

    Handles None (→ SQL NULL), pre-serialised JSON strings (parsed back),
    and plain Python objects (dicts, lists).
    """
    if value is None:
        return None
    if isinstance(value, str):
        return Json(json.loads(value), dumps=lambda v: json.dumps(v, default=_json_default))
    return Json(value, dumps=lambda v: json.dumps(v, default=_json_default))


def _json_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serialisable")


# ── public API ────────────────────────────────────────────────────────────────

def create_payroll_snapshot(
    payroll_run_id: str,
    workspace_id: str,
    component_metadata_rows: list[dict],
    client_override_rows: list[dict],
    employees_data: list[dict],
) -> None:
    """Freeze component metadata, client overrides, and employee contracts at run time.

    Uses psycopg2 execute_values for all three batches — single round-trip per
    table regardless of row count, avoiding the N×latency problem from executemany.

    D3: all three INSERT batches share a single raw_conn.commit(). Any INSERT
    failure propagates — no partial commit. The orphaned DRAFT run has no snapshot
    rows so validate_snapshot_complete() blocks any retry attempt on it.

    Idempotent: ON CONFLICT DO NOTHING — safe to call twice on the same run_id.
    """
    raw_conn = engine.raw_connection()
    try:
        cursor = raw_conn.cursor()

        # 1. component_metadata_snapshot
        if component_metadata_rows:
            rows = [
                (
                    payroll_run_id,
                    row["component_code"],
                    row.get("component_class"),
                    row.get("calculation_method"),
                    row.get("execution_priority"),
                    row.get("is_active"),
                    _as_json(row.get("metadata_json")),
                )
                for row in component_metadata_rows
            ]
            execute_values(
                cursor,
                """
                INSERT INTO component_metadata_snapshot
                    (payroll_run_id, component_code, component_class,
                     calculation_method, execution_priority, is_active, metadata_json)
                VALUES %s
                ON CONFLICT (payroll_run_id, component_code) DO NOTHING
                """,
                rows,
            )

        # 2. client_component_metadata_snapshot
        if client_override_rows:
            rows = [
                (
                    payroll_run_id,
                    workspace_id,
                    row["component_code"],
                    _as_json(row["overrides_json"]),
                    row["proration_strategy"],
                    row.get("is_active", True),
                )
                for row in client_override_rows
            ]
            execute_values(
                cursor,
                """
                INSERT INTO client_component_metadata_snapshot
                    (payroll_run_id, workspace_id, component_code,
                     overrides_json, proration_strategy, is_active)
                VALUES %s
                ON CONFLICT (payroll_run_id, component_code) DO NOTHING
                """,
                rows,
            )

        # 3. employee_contract_snapshot (D1: salary_definition_id frozen)
        if employees_data:
            rows = [
                (
                    payroll_run_id,
                    emp["employee_id"],
                    emp["salary_definition_id"],
                    _as_json(emp.get("components_jsonb")),
                    emp.get("start_date") or emp.get("contract_start"),
                    emp.get("end_date") or emp.get("contract_end"),
                    emp.get("shift_type"),
                    emp.get("grade_id"),
                    _as_json(emp.get("grade_jsonb")),
                )
                for emp in employees_data
            ]
            execute_values(
                cursor,
                """
                INSERT INTO employee_contract_snapshot
                    (payroll_run_id, employee_id, salary_definition_id,
                     components_jsonb, contract_start, contract_end,
                     shift_type, grade_id, grade_jsonb)
                VALUES %s
                ON CONFLICT (payroll_run_id, employee_id) DO NOTHING
                """,
                rows,
            )

        raw_conn.commit()
    finally:
        cursor.close()
        raw_conn.close()


def validate_snapshot_complete(db, payroll_run_id: str) -> None:
    """Raise ValueError if snapshot is absent or incomplete.

    D6: callers must hard-fail (raise), not silently skip, when this raises.
    Called in _build_shared_context() before any retry calculation begins.

    Checks employee_contract_snapshot and component_metadata_snapshot only.
    client_component_metadata_snapshot is intentionally excluded: a workspace
    with zero component overrides is valid, so an empty override table is not
    an error signal.
    """
    from sqlalchemy import text
    row = db.execute(
        text("""
            SELECT
                COUNT(*) FILTER (WHERE src = 'emp')  AS emp_count,
                COUNT(*) FILTER (WHERE src = 'comp') AS comp_count
            FROM (
                SELECT 'emp'  AS src FROM employee_contract_snapshot  WHERE payroll_run_id = :run_id
                UNION ALL
                SELECT 'comp' AS src FROM component_metadata_snapshot WHERE payroll_run_id = :run_id
            ) t
        """),
        {"run_id": payroll_run_id},
    ).fetchone()

    emp_count  = row[0]
    comp_count = row[1]

    if emp_count == 0 or comp_count == 0:
        raise ValueError(
            f"Run {payroll_run_id} predates snapshot engine — open a correction run"
        )

    _log.debug(
        "Snapshot validated for run %s: %d employee rows, %d component rows",
        payroll_run_id,
        emp_count,
        comp_count,
    )
