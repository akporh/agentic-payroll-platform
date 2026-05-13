"""
Workspace Payroll Config Repository.

Versioned-row pattern: a workspace may have multiple rows, each with a
different effective_from date.  The active config is the row with the
greatest effective_from that is <= CURRENT_DATE.  If no row exists the
caller receives a dict of platform defaults.
"""

from sqlalchemy import text

from backend.infra.db.session import SessionLocal

_DEFAULTS = {
    "ph_mode":               "FILE_BASED",
    "ph_rate_code":          "OT005",
    "saturday_ph_rule":      "PH_TAKES_PRECEDENCE",
    "sunday_ph_rule":        "PH_TAKES_PRECEDENCE",
    "d3_leave_overlap_rule": "LEAVE_ABSORBS_PH",
    "d4_absence_rule":       "ABSENT_IS_DEDUCTIBLE",
    "timesheet_enabled":     False,
}


def get_workspace_payroll_config(workspace_id: str) -> dict:
    """Return the active config row for a workspace, or platform defaults.

    Active = greatest effective_from <= CURRENT_DATE.
    Returns a plain dict — never None.
    """
    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                SELECT
                    config_id, workspace_id, effective_from,
                    ph_mode, ph_rate_code,
                    saturday_ph_rule, sunday_ph_rule,
                    d3_leave_overlap_rule, d4_absence_rule,
                    timesheet_enabled,
                    updated_at, updated_by
                FROM workspace_payroll_config
                WHERE workspace_id  = :wid
                  AND effective_from <= CURRENT_DATE
                ORDER BY effective_from DESC
                LIMIT 1
            """),
            {"wid": workspace_id},
        ).fetchone()

        if row is None:
            return {"workspace_id": workspace_id, **_DEFAULTS}

        return {
            "config_id":             str(row[0]),
            "workspace_id":          str(row[1]),
            "effective_from":        row[2].isoformat(),
            "ph_mode":               row[3],
            "ph_rate_code":          row[4],
            "saturday_ph_rule":      row[5],
            "sunday_ph_rule":        row[6],
            "d3_leave_overlap_rule": row[7],
            "d4_absence_rule":       row[8],
            "timesheet_enabled":     bool(row[9]) if row[9] is not None else False,
            "updated_at":            row[10].isoformat() if row[10] else None,
            "updated_by":            str(row[11]) if row[11] else None,
        }
    finally:
        db.close()


def upsert_workspace_payroll_config(
    workspace_id: str,
    effective_from: str,
    *,
    ph_mode: str | None = None,
    ph_rate_code: str | None = None,
    saturday_ph_rule: str | None = None,
    sunday_ph_rule: str | None = None,
    d3_leave_overlap_rule: str | None = None,
    d4_absence_rule: str | None = None,
    timesheet_enabled: bool | None = None,
    updated_by: str | None = None,
) -> dict:
    """Insert a new versioned config row, or update the row for an existing
    (workspace_id, effective_from) pair.

    Only fields explicitly passed (non-None) are written; the rest keep their
    current DB value via EXCLUDED fallback.

    Returns the resulting config dict.
    """
    db = SessionLocal()
    try:
        db.execute(
            text("""
                INSERT INTO workspace_payroll_config (
                    workspace_id, effective_from,
                    ph_mode, ph_rate_code,
                    saturday_ph_rule, sunday_ph_rule,
                    d3_leave_overlap_rule, d4_absence_rule,
                    timesheet_enabled,
                    updated_at, updated_by
                )
                VALUES (
                    :wid, :effective_from,
                    COALESCE(:ph_mode,               'FILE_BASED'),
                    COALESCE(:ph_rate_code,           'OT005'),
                    COALESCE(:saturday_ph_rule,       'PH_TAKES_PRECEDENCE'),
                    COALESCE(:sunday_ph_rule,         'PH_TAKES_PRECEDENCE'),
                    COALESCE(:d3_leave_overlap_rule,  'LEAVE_ABSORBS_PH'),
                    COALESCE(:d4_absence_rule,        'ABSENT_IS_DEDUCTIBLE'),
                    COALESCE(:timesheet_enabled,      FALSE),
                    now(),
                    :updated_by
                )
                ON CONFLICT (workspace_id, effective_from) DO UPDATE
                SET
                    ph_mode               = COALESCE(:ph_mode,              EXCLUDED.ph_mode),
                    ph_rate_code          = COALESCE(:ph_rate_code,         EXCLUDED.ph_rate_code),
                    saturday_ph_rule      = COALESCE(:saturday_ph_rule,     EXCLUDED.saturday_ph_rule),
                    sunday_ph_rule        = COALESCE(:sunday_ph_rule,       EXCLUDED.sunday_ph_rule),
                    d3_leave_overlap_rule = COALESCE(:d3_leave_overlap_rule,EXCLUDED.d3_leave_overlap_rule),
                    d4_absence_rule       = COALESCE(:d4_absence_rule,      EXCLUDED.d4_absence_rule),
                    timesheet_enabled     = COALESCE(:timesheet_enabled,    EXCLUDED.timesheet_enabled),
                    updated_at            = now(),
                    updated_by            = :updated_by
            """),
            {
                "wid":                   workspace_id,
                "effective_from":        effective_from,
                "ph_mode":               ph_mode,
                "ph_rate_code":          ph_rate_code,
                "saturday_ph_rule":      saturday_ph_rule,
                "sunday_ph_rule":        sunday_ph_rule,
                "d3_leave_overlap_rule": d3_leave_overlap_rule,
                "d4_absence_rule":       d4_absence_rule,
                "timesheet_enabled":     timesheet_enabled,
                "updated_by":            updated_by,
            },
        )
        db.commit()
    finally:
        db.close()

    return get_workspace_payroll_config(workspace_id)
