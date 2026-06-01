import json
import logging
from decimal import Decimal

from sqlalchemy import text

_log = logging.getLogger(__name__)


# ── helpers ───────────────────────────────────────────────────────────────────

def _jsonb(value) -> str | None:
    """Serialise a value to a JSON string for CAST(:x AS jsonb) placeholders."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, default=_json_default)


def _json_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serialisable")


# ── public API ────────────────────────────────────────────────────────────────

def create_payroll_snapshot(
    db,
    payroll_run_id: str,
    workspace_id: str,
    component_metadata_rows: list[dict],
    client_override_rows: list[dict],
    employees_data: list[dict],
) -> None:
    """Freeze component metadata, client overrides, and employee contracts at run time.

    D3: all three INSERT batches share a single db.commit(). Any INSERT failure
    propagates — no partial commit. The caller treats any exception as HTTP 500;
    the orphaned DRAFT run has no snapshot rows so validate_snapshot_complete()
    blocks any retry attempt on it.

    Idempotent: ON CONFLICT DO NOTHING — safe to call twice on the same run_id.

    client_override_rows must be a list of dicts with keys:
        component_code, overrides_json, proration_strategy
    """
    # 1. component_metadata_snapshot
    if component_metadata_rows:
        db.execute(
            text("""
                INSERT INTO component_metadata_snapshot
                    (payroll_run_id, component_code, component_class,
                     calculation_method, execution_priority, is_active, metadata_json)
                VALUES
                    (:run_id, :code, :cls, :method, :priority, :active, CAST(:meta AS jsonb))
                ON CONFLICT (payroll_run_id, component_code) DO NOTHING
            """),
            [
                {
                    "run_id": payroll_run_id,
                    "code": row["component_code"],
                    "cls": row.get("component_class"),
                    "method": row.get("calculation_method"),
                    "priority": row.get("execution_priority"),
                    "active": row.get("is_active"),
                    "meta": _jsonb(row.get("metadata_json")),
                }
                for row in component_metadata_rows
            ],
        )

    # 2. client_component_metadata_snapshot
    if client_override_rows:
        db.execute(
            text("""
                INSERT INTO client_component_metadata_snapshot
                    (payroll_run_id, workspace_id, component_code,
                     overrides_json, proration_strategy)
                VALUES
                    (:run_id, :wid, :code, CAST(:overrides AS jsonb), :strategy)
                ON CONFLICT (payroll_run_id, component_code) DO NOTHING
            """),
            [
                {
                    "run_id": payroll_run_id,
                    "wid": workspace_id,
                    "code": row["component_code"],
                    "overrides": _jsonb(row["overrides_json"]),
                    "strategy": row["proration_strategy"],
                }
                for row in client_override_rows
            ],
        )

    # 3. employee_contract_snapshot (D1: salary_definition_id frozen)
    if employees_data:
        db.execute(
            text("""
                INSERT INTO employee_contract_snapshot
                    (payroll_run_id, employee_id, salary_definition_id,
                     components_jsonb, contract_start, contract_end,
                     shift_type, grade_id, grade_jsonb)
                VALUES
                    (:run_id, :eid, :sal_def_id,
                     CAST(:components AS jsonb), :start, :end,
                     :shift, :grade_id, CAST(:grade_json AS jsonb))
                ON CONFLICT (payroll_run_id, employee_id) DO NOTHING
            """),
            [
                {
                    "run_id": payroll_run_id,
                    "eid": emp["employee_id"],
                    "sal_def_id": emp["salary_definition_id"],
                    "components": _jsonb(emp.get("components_jsonb")),
                    "start": emp.get("start_date") or emp.get("contract_start"),
                    "end": emp.get("end_date") or emp.get("contract_end"),
                    "shift": emp.get("shift_type"),
                    "grade_id": emp.get("grade_id"),
                    "grade_json": _jsonb(emp.get("grade_jsonb")),
                }
                for emp in employees_data
            ],
        )

    db.commit()  # D3: single commit — atomicity across all three tables


def validate_snapshot_complete(db, payroll_run_id: str) -> None:
    """Raise ValueError if snapshot is absent or incomplete.

    D6: callers must hard-fail (raise), not silently skip, when this raises.
    Called in _build_shared_context() before any retry calculation begins.

    Checks employee_contract_snapshot and component_metadata_snapshot only.
    client_component_metadata_snapshot is intentionally excluded: a workspace
    with zero component overrides is valid, so an empty override table is not
    an error signal.
    """
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
