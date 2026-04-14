"""
Public Holiday Repository.

Merges Tier-1 national holidays (national_public_holiday) and
workspace-specific additions (workspace_public_holiday) into a single
effective list for a given pay period.

country_code guard: if workspace.country_code IS NULL the national
query returns no rows and the caller receives only workspace-specific
holidays (or an empty list).
"""

from sqlalchemy import text

from backend.infra.db.session import SessionLocal


def get_effective_ph_list(
    workspace_id: str,
    country_code: str | None,
    period_start: str,
    period_end: str,
) -> list[dict]:
    """Return the merged public holiday list for a pay period.

    Args:
        workspace_id:  Owning workspace UUID.
        country_code:  ISO country code (e.g. 'NG').  If None, national
                       holidays are skipped and a warning should be raised
                       by the caller (PH-11 pre-flight).
        period_start:  ISO date string, inclusive.
        period_end:    ISO date string, inclusive.

    Returns:
        List of dicts: [{date, name, source}]
        source is 'NATIONAL' or 'WORKSPACE'.
    """
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT holiday_date, name, 'NATIONAL' AS source
                FROM   national_public_holiday
                WHERE  country_code  = :country_code
                  AND  holiday_date >= :start
                  AND  holiday_date <= :end

                UNION ALL

                SELECT holiday_date, name, 'WORKSPACE' AS source
                FROM   workspace_public_holiday
                WHERE  workspace_id  = :workspace_id
                  AND  holiday_date >= :start
                  AND  holiday_date <= :end

                ORDER BY holiday_date
            """),
            {
                "country_code": country_code or "__none__",
                "workspace_id": workspace_id,
                "start":        period_start,
                "end":          period_end,
            },
        ).fetchall()

        return [
            {
                "date":   row[0],
                "name":   row[1],
                "source": row[2],
            }
            for row in rows
        ]
    finally:
        db.close()


def list_workspace_holidays(
    workspace_id: str,
    country_code: str | None,
    year: int | None = None,
) -> list[dict]:
    """Return public holidays visible to a workspace, optionally filtered by year.

    Returns both NATIONAL (Tier-1) and WORKSPACE (Tier-2) rows so operators
    can see the full picture when managing custom additions.

    Args:
        workspace_id:  Owning workspace UUID.
        country_code:  ISO country code for national holiday lookup.  When None,
                       only workspace-specific holidays are returned.
        year:          Optional calendar year filter (e.g. 2026).
    """
    db = SessionLocal()
    try:
        year_filter_national  = "AND EXTRACT(YEAR FROM holiday_date) = :year" if year else ""
        year_filter_workspace = "AND EXTRACT(YEAR FROM holiday_date) = :year" if year else ""

        rows = db.execute(
            text(f"""
                SELECT holiday_date, name, 'NATIONAL' AS source, NULL AS holiday_id
                FROM   national_public_holiday
                WHERE  country_code = :country_code
                  {year_filter_national}

                UNION ALL

                SELECT holiday_date, name, 'WORKSPACE' AS source, holiday_id
                FROM   workspace_public_holiday
                WHERE  workspace_id = :workspace_id
                  {year_filter_workspace}

                ORDER BY holiday_date
            """),
            {
                "country_code": country_code or "__none__",
                "workspace_id": workspace_id,
                "year":         year,
            },
        ).fetchall()

        return [
            {
                "holiday_id": str(row[3]) if row[3] else None,
                "date":       row[0].isoformat(),
                "name":       row[1],
                "source":     row[2],
            }
            for row in rows
        ]
    finally:
        db.close()


def add_workspace_holiday(
    workspace_id: str,
    holiday_date: str,
    name: str,
) -> dict:
    """Add a workspace-specific public holiday.

    Raises:
        ValueError: If a holiday already exists on that date for the workspace.
    """
    db = SessionLocal()
    try:
        existing = db.execute(
            text("""
                SELECT 1 FROM workspace_public_holiday
                WHERE workspace_id = :wid AND holiday_date = :date
            """),
            {"wid": workspace_id, "date": holiday_date},
        ).fetchone()

        if existing:
            raise ValueError(
                f"A holiday already exists on {holiday_date} for workspace {workspace_id}."
            )

        row = db.execute(
            text("""
                INSERT INTO workspace_public_holiday
                    (workspace_id, holiday_date, name, created_at)
                VALUES (:wid, :date, :name, now())
                RETURNING holiday_id, workspace_id, holiday_date, name, created_at
            """),
            {"wid": workspace_id, "date": holiday_date, "name": name},
        ).fetchone()

        db.commit()

        return {
            "holiday_id":   str(row[0]),
            "workspace_id": str(row[1]),
            "holiday_date": row[2].isoformat(),
            "name":         row[3],
            "created_at":   row[4].isoformat(),
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_workspace_holiday(holiday_id: str, workspace_id: str) -> bool:
    """Delete a workspace-specific public holiday.

    Workspace-scoped: will not delete a holiday belonging to another workspace.

    Returns:
        True if a row was deleted, False if not found.
    """
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                DELETE FROM workspace_public_holiday
                WHERE holiday_id   = :hid
                  AND workspace_id = :wid
            """),
            {"hid": holiday_id, "wid": workspace_id},
        )
        db.commit()
        return result.rowcount > 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
