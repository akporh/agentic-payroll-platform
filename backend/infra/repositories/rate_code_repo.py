"""
Rate Code Registry Repository.

Workspace-specific rows take precedence over platform seeds (workspace_id IS NULL).
"""

from sqlalchemy import text

from backend.infra.db.session import SessionLocal


def get_rate_code(workspace_id: str, code: str) -> dict | None:
    """Return the effective rate code for a workspace.

    Workspace-specific row wins if it exists; falls back to platform seed
    (workspace_id IS NULL).  Returns None if neither exists.
    """
    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                SELECT
                    rate_code_id, workspace_id, code,
                    multiplier, unit, base, description, is_active
                FROM rate_code_registry
                WHERE code = :code
                  AND (workspace_id = :wid OR workspace_id IS NULL)
                  AND is_active = TRUE
                ORDER BY workspace_id NULLS LAST
                LIMIT 1
            """),
            {"code": code, "wid": workspace_id},
        ).fetchone()

        if row is None:
            return None

        return {
            "rate_code_id": str(row[0]),
            "workspace_id": str(row[1]) if row[1] else None,
            "code":         row[2],
            "multiplier":   row[3],
            "unit":         row[4],
            "base":         row[5],
            "description":  row[6],
            "is_active":    row[7],
        }
    finally:
        db.close()


def create_rate_code(
    workspace_id: str,
    code: str,
    multiplier: float,
    unit: str,
    base: str,
    description: str | None = None,
) -> dict:
    """Insert a workspace-specific rate code row.

    Raises:
        ValueError: If a rate code with the same code already exists for this workspace.
    """
    db = SessionLocal()
    try:
        existing = db.execute(
            text("""
                SELECT 1 FROM rate_code_registry
                WHERE workspace_id = :wid AND code = :code
            """),
            {"wid": workspace_id, "code": code},
        ).fetchone()

        if existing:
            raise ValueError(
                f"Rate code '{code}' already exists for workspace {workspace_id}."
            )

        row = db.execute(
            text("""
                INSERT INTO rate_code_registry
                    (workspace_id, code, multiplier, unit, base, description, is_active)
                VALUES (:wid, :code, :multiplier, :unit, :base, :description, TRUE)
                RETURNING rate_code_id, workspace_id, code, multiplier, unit, base,
                          description, is_active
            """),
            {
                "wid":         workspace_id,
                "code":        code,
                "multiplier":  multiplier,
                "unit":        unit,
                "base":        base,
                "description": description,
            },
        ).fetchone()

        db.commit()

        return {
            "rate_code_id": str(row[0]),
            "workspace_id": str(row[1]) if row[1] else None,
            "code":         row[2],
            "multiplier":   row[3],
            "unit":         row[4],
            "base":         row[5],
            "description":  row[6],
            "is_active":    row[7],
            "is_platform":  False,
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_rate_code(workspace_id: str, code: str) -> bool:
    """Soft-delete (deactivate) a workspace-specific rate code.

    Returns True if deactivated, False if the row was not found.
    Raises ValueError if the row exists but belongs to the platform
    (workspace_id IS NULL) — platform seeds are read-only.
    """
    db = SessionLocal()
    try:
        # Check if a platform seed with this code exists
        platform_row = db.execute(
            text("""
                SELECT 1 FROM rate_code_registry
                WHERE workspace_id IS NULL AND code = :code AND is_active = TRUE
            """),
            {"code": code},
        ).fetchone()

        if platform_row:
            raise ValueError(
                f"Rate code '{code}' is a platform seed and cannot be deleted."
            )

        result = db.execute(
            text("""
                UPDATE rate_code_registry
                SET is_active = FALSE
                WHERE workspace_id = :wid AND code = :code AND is_active = TRUE
            """),
            {"wid": workspace_id, "code": code},
        )
        db.commit()
        return result.rowcount > 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def list_rate_codes(workspace_id: str) -> list[dict]:
    """Return all active rate codes visible to a workspace.

    Merges platform seeds and workspace overrides.  Workspace rows shadow
    platform seeds with the same code.
    """
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT DISTINCT ON (code)
                    rate_code_id, workspace_id, code,
                    multiplier, unit, base, description, is_active
                FROM rate_code_registry
                WHERE (workspace_id = :wid OR workspace_id IS NULL)
                  AND is_active = TRUE
                ORDER BY code, workspace_id NULLS LAST
            """),
            {"wid": workspace_id},
        ).fetchall()

        return [
            {
                "rate_code_id": str(r[0]),
                "workspace_id": str(r[1]) if r[1] else None,
                "code":         r[2],
                "multiplier":   r[3],
                "unit":         r[4],
                "base":         r[5],
                "description":  r[6],
                "is_active":    r[7],
                "is_platform":  r[1] is None,
            }
            for r in rows
        ]
    finally:
        db.close()
