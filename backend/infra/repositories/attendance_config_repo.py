"""
Attendance Config Repository.

Loads attendance_code_config and attendance_policy_config for a workspace.
Every query is scoped to workspace_id — no cross-workspace access is possible.
"""

from sqlalchemy import text
from backend.infra.db.session import SessionLocal


def get_attendance_codes(workspace_id: str) -> list[dict]:
    """Return all attendance codes for a workspace, left-joined with their policy.

    Codes with no policy row are included — caller can detect orphans by checking
    if policy fields are None.
    """
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT
                    acc.attendance_code_config_id,
                    acc.client_code,
                    acc.description,
                    acc.category,
                    acc.is_active,
                    acc.updated_at,
                    apc.attendance_policy_config_id,
                    apc.counts_as_paid,
                    apc.counts_towards_ot_threshold,
                    apc.hours_equivalent,
                    apc.unit_fraction,
                    apc.eligible_for_shift_allowance,
                    apc.eligible_for_ot,
                    apc.updated_at AS policy_updated_at
                FROM attendance_code_config acc
                LEFT JOIN attendance_policy_config apc
                       ON apc.workspace_id = acc.workspace_id
                      AND apc.client_code  = acc.client_code
                WHERE acc.workspace_id = :wid
                ORDER BY acc.client_code
            """),
            {"wid": workspace_id},
        ).fetchall()

        return [
            {
                "attendance_code_config_id":  str(r[0]),
                "client_code":                r[1],
                "description":                r[2],
                "category":                   r[3],
                "is_active":                  r[4],
                "updated_at":                 r[5].isoformat() if r[5] else None,
                "has_policy":                 r[6] is not None,
                "attendance_policy_config_id": str(r[6]) if r[6] else None,
                "counts_as_paid":             r[7],
                "counts_towards_ot_threshold": r[8],
                "hours_equivalent":           str(r[9]) if r[9] is not None else None,
                "unit_fraction":              str(r[10]) if r[10] is not None else None,
                "eligible_for_shift_allowance": r[11],
                "eligible_for_ot":            r[12],
                "policy_updated_at":          r[13].isoformat() if r[13] else None,
            }
            for r in rows
        ]
    finally:
        db.close()


def get_attendance_policies_for_derivation(workspace_id: str) -> dict[str, dict]:
    """Return {client_code: policy_dict} for all codes that have a policy row.

    Used by the derivation service. Only returns rows with a complete policy
    (INNER JOIN). Orphaned codes (code but no policy) are NOT included — the
    derivation service detects them separately via prefetch validation.
    """
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT
                    apc.client_code,
                    apc.counts_as_paid,
                    apc.counts_towards_ot_threshold,
                    apc.hours_equivalent,
                    apc.unit_fraction,
                    apc.eligible_for_shift_allowance,
                    apc.eligible_for_ot,
                    acc.category,
                    acc.is_active
                FROM attendance_policy_config apc
                JOIN attendance_code_config acc
                  ON acc.workspace_id = apc.workspace_id
                 AND acc.client_code  = apc.client_code
                WHERE apc.workspace_id = :wid
            """),
            {"wid": workspace_id},
        ).fetchall()

        return {
            r[0]: {
                "counts_as_paid":               r[1],
                "counts_towards_ot_threshold":  r[2],
                "hours_equivalent":             r[3],
                "unit_fraction":                r[4],
                "eligible_for_shift_allowance": r[5],
                "eligible_for_ot":              r[6],
                "category":                     r[7],
                "is_active":                    r[8],
            }
            for r in rows
        }
    finally:
        db.close()


def get_all_code_client_codes(workspace_id: str) -> set[str]:
    """Return the set of all client_codes in attendance_code_config for the workspace."""
    db = SessionLocal()
    try:
        rows = db.execute(
            text("SELECT client_code FROM attendance_code_config WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).fetchall()
        return {r[0] for r in rows}
    finally:
        db.close()


def upsert_attendance_code(
    workspace_id: str,
    client_code: str,
    *,
    description: str | None = None,
    category: str | None = None,
    is_active: bool | None = None,
) -> dict:
    """Create or update an attendance code.

    category is required on INSERT (new code) and MUST NOT be passed on
    UPDATE — enforced at the API layer, not here.
    """
    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                INSERT INTO attendance_code_config
                    (attendance_code_config_id, workspace_id, client_code,
                     description, category, is_active)
                VALUES
                    (gen_random_uuid(), :wid, :code,
                     :description, :category, COALESCE(:is_active, TRUE))
                ON CONFLICT (workspace_id, client_code) DO UPDATE
                SET
                    description = COALESCE(:description, EXCLUDED.description),
                    is_active   = COALESCE(:is_active,   EXCLUDED.is_active),
                    updated_at  = now()
                RETURNING attendance_code_config_id, client_code, description, category, is_active
            """),
            {
                "wid":         workspace_id,
                "code":        client_code,
                "description": description,
                "category":    category,
                "is_active":   is_active,
            },
        ).fetchone()
        db.commit()
        return {
            "attendance_code_config_id": str(row[0]),
            "client_code":               row[1],
            "description":               row[2],
            "category":                  row[3],
            "is_active":                 row[4],
        }
    finally:
        db.close()


def upsert_attendance_policy(
    workspace_id: str,
    client_code: str,
    *,
    counts_as_paid: bool | None = None,
    counts_towards_ot_threshold: bool | None = None,
    hours_equivalent=None,
    unit_fraction=None,
    eligible_for_shift_allowance: bool | None = None,
    eligible_for_ot: bool | None = None,
) -> dict:
    """Create or update an attendance policy for a code."""
    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                INSERT INTO attendance_policy_config
                    (attendance_policy_config_id, workspace_id, client_code,
                     counts_as_paid, counts_towards_ot_threshold,
                     hours_equivalent, unit_fraction,
                     eligible_for_shift_allowance, eligible_for_ot)
                VALUES
                    (gen_random_uuid(), :wid, :code,
                     COALESCE(:counts_as_paid, TRUE),
                     COALESCE(:counts_towards_ot_threshold, TRUE),
                     :hours_equivalent, :unit_fraction,
                     COALESCE(:eligible_for_shift_allowance, FALSE),
                     COALESCE(:eligible_for_ot, FALSE))
                ON CONFLICT (workspace_id, client_code) DO UPDATE
                SET
                    counts_as_paid               = COALESCE(:counts_as_paid,              EXCLUDED.counts_as_paid),
                    counts_towards_ot_threshold  = COALESCE(:counts_towards_ot_threshold, EXCLUDED.counts_towards_ot_threshold),
                    hours_equivalent             = COALESCE(:hours_equivalent,             EXCLUDED.hours_equivalent),
                    unit_fraction                = COALESCE(:unit_fraction,                EXCLUDED.unit_fraction),
                    eligible_for_shift_allowance = COALESCE(:eligible_for_shift_allowance, EXCLUDED.eligible_for_shift_allowance),
                    eligible_for_ot              = COALESCE(:eligible_for_ot,              EXCLUDED.eligible_for_ot),
                    updated_at                   = now()
                RETURNING attendance_policy_config_id, client_code,
                          counts_as_paid, counts_towards_ot_threshold,
                          hours_equivalent, unit_fraction,
                          eligible_for_shift_allowance, eligible_for_ot
            """),
            {
                "wid":                          workspace_id,
                "code":                         client_code,
                "counts_as_paid":               counts_as_paid,
                "counts_towards_ot_threshold":  counts_towards_ot_threshold,
                "hours_equivalent":             hours_equivalent,
                "unit_fraction":                unit_fraction,
                "eligible_for_shift_allowance": eligible_for_shift_allowance,
                "eligible_for_ot":              eligible_for_ot,
            },
        ).fetchone()
        db.commit()
        return {
            "attendance_policy_config_id":  str(row[0]),
            "client_code":                  row[1],
            "counts_as_paid":               row[2],
            "counts_towards_ot_threshold":  row[3],
            "hours_equivalent":             str(row[4]) if row[4] is not None else None,
            "unit_fraction":                str(row[5]) if row[5] is not None else None,
            "eligible_for_shift_allowance": row[6],
            "eligible_for_ot":              row[7],
        }
    finally:
        db.close()


def seed_from_platform_templates(workspace_id: str) -> str | None:
    """Seed workspace attendance codes and policies from the latest platform template.

    Uses ON CONFLICT DO NOTHING — existing workspace rows are not overwritten.
    Updates workspace.attendance_template_version to the latest version tag.
    Returns the version tag that was seeded, or None if no platform template exists.
    """
    db = SessionLocal()
    try:
        version_row = db.execute(
            text("""
                SELECT version_tag
                FROM platform_attendance_template_version
                ORDER BY released_at DESC
                LIMIT 1
            """),
        ).fetchone()

        if version_row is None:
            return None

        latest_version = version_row[0]

        # Seed code rows
        db.execute(
            text("""
                INSERT INTO attendance_code_config
                    (attendance_code_config_id, workspace_id, client_code,
                     description, category, is_active)
                SELECT
                    gen_random_uuid(), :wid, t.client_code,
                    t.description, t.category, t.is_active
                FROM platform_attendance_code_template t
                ON CONFLICT (workspace_id, client_code) DO NOTHING
            """),
            {"wid": workspace_id},
        )

        # Seed policy rows
        db.execute(
            text("""
                INSERT INTO attendance_policy_config
                    (attendance_policy_config_id, workspace_id, client_code,
                     counts_as_paid, counts_towards_ot_threshold,
                     hours_equivalent, unit_fraction,
                     eligible_for_shift_allowance, eligible_for_ot)
                SELECT
                    gen_random_uuid(), :wid, t.client_code,
                    t.counts_as_paid, t.counts_towards_ot_threshold,
                    t.hours_equivalent, t.unit_fraction,
                    t.eligible_for_shift_allowance, t.eligible_for_ot
                FROM platform_attendance_policy_template t
                ON CONFLICT (workspace_id, client_code) DO NOTHING
            """),
            {"wid": workspace_id},
        )

        # Track which template version this workspace is on
        db.execute(
            text("""
                UPDATE workspace
                SET attendance_template_version = :version
                WHERE workspace_id = :wid
            """),
            {"wid": workspace_id, "version": latest_version},
        )

        db.commit()
        return latest_version
    finally:
        db.close()


def get_workspace_template_version(workspace_id: str) -> str | None:
    """Return the attendance_template_version for the workspace, or None."""
    db = SessionLocal()
    try:
        row = db.execute(
            text("SELECT attendance_template_version FROM workspace WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).fetchone()
        return row[0] if row else None
    finally:
        db.close()


def get_latest_platform_template_version() -> str | None:
    """Return the latest platform template version tag."""
    db = SessionLocal()
    try:
        row = db.execute(
            text("SELECT version_tag FROM platform_attendance_template_version ORDER BY released_at DESC LIMIT 1"),
        ).fetchone()
        return row[0] if row else None
    finally:
        db.close()
