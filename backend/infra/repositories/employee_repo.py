"""Employee Repository — raw SQL for employee and employee_contract tables.

All functions accept a `db` session from the caller so they can participate
in an outer transaction (e.g. the onboarding commit route).  Callers own
commit/rollback.
"""

from datetime import date
from uuid import uuid4

from psycopg2.extras import Json
from sqlalchemy import text


# ---------------------------------------------------------------------------
# Reads
# ---------------------------------------------------------------------------

def get_employees_with_contracts(db, workspace_id: str) -> list[dict]:
    """Return all employees with their most-recent contract (LATERAL join)."""
    rows = db.execute(
        text("""
            SELECT
                e.employee_id,
                e.employee_number,
                e.full_name,
                e.status,
                e.created_at,
                ec.contract_id,
                ec.salary_definition_id,
                sd.code          AS salary_definition_code,
                ec.grade_id,
                g.grade_code,
                ec.designation_id,
                d.designation_code,
                ec.start_date,
                ec.end_date,
                ec.shift_type,
                ec.state_of_tax,
                ec.skill_level,
                ec.is_union_member,
                ec.change_reason,
                ec.imported_grade_label,
                ec.imported_designation_label
            FROM employee e
            LEFT JOIN LATERAL (
                SELECT ec2.*
                FROM   employee_contract ec2
                WHERE  ec2.employee_id = e.employee_id
                ORDER  BY COALESCE(ec2.end_date, '9999-12-31') DESC,
                          ec2.start_date DESC NULLS LAST
                LIMIT  1
            ) ec ON true
            LEFT JOIN salary_definition sd
                   ON sd.salary_definition_id = ec.salary_definition_id
            LEFT JOIN grade g ON g.grade_id = ec.grade_id
            LEFT JOIN designation d ON d.designation_id = ec.designation_id
            WHERE e.workspace_id = :wid
            ORDER BY e.full_name
        """),
        {"wid": workspace_id},
    ).fetchall()

    return [_employee_row_to_dict(r) for r in rows]


def get_employee_with_contract_history(
    db, workspace_id: str, employee_id: str
) -> dict | None:
    """Return a single employee plus all contracts ordered newest first."""
    emp = db.execute(
        text("""
            SELECT employee_id, employee_number, full_name, status,
                   created_at, personal_details_encrypted
            FROM   employee
            WHERE  workspace_id = :wid
              AND  employee_id  = CAST(:eid AS uuid)
        """),
        {"wid": workspace_id, "eid": employee_id},
    ).fetchone()

    if emp is None:
        return None

    contracts = db.execute(
        text("""
            SELECT
                ec.contract_id,
                ec.salary_definition_id,
                sd.code AS salary_definition_code,
                ec.grade_id,
                g.grade_code,
                ec.designation_id,
                d.designation_code,
                ec.start_date,
                ec.end_date,
                ec.shift_type,
                ec.state_of_tax,
                ec.skill_level,
                ec.is_union_member,
                ec.change_reason
            FROM   employee_contract ec
            LEFT JOIN salary_definition sd
                   ON sd.salary_definition_id = ec.salary_definition_id
            LEFT JOIN grade g ON g.grade_id = ec.grade_id
            LEFT JOIN designation d ON d.designation_id = ec.designation_id
            WHERE  ec.employee_id = CAST(:eid AS uuid)
            ORDER  BY COALESCE(ec.end_date, '9999-12-31') DESC,
                      ec.start_date DESC NULLS LAST
        """),
        {"eid": employee_id},
    ).fetchall()

    return {
        "employee_id":      str(emp[0]),
        "employee_number":  emp[1],
        "full_name":        emp[2],
        "status":           emp[3],
        "created_at":       emp[4].isoformat() if emp[4] else None,
        "personal_details": emp[5],
        "contracts":        [_contract_row_to_dict(r) for r in contracts],
    }


def get_current_contract(db, employee_id: str) -> dict | None:
    """Return the most-recent contract for an employee."""
    row = db.execute(
        text("""
            SELECT contract_id, salary_definition_id, start_date, end_date
            FROM   employee_contract
            WHERE  employee_id = CAST(:eid AS uuid)
            ORDER  BY COALESCE(end_date, '9999-12-31') DESC,
                      start_date DESC NULLS LAST
            LIMIT  1
        """),
        {"eid": employee_id},
    ).fetchone()

    if row is None:
        return None
    return {
        "contract_id":          str(row[0]),
        "salary_definition_id": str(row[1]) if row[1] else None,
        "start_date":           row[2],
        "end_date":             row[3],
    }


# ---------------------------------------------------------------------------
# Writes
# ---------------------------------------------------------------------------

def insert_employee(
    db,
    workspace_id: str,
    employee_id: str,
    full_name: str,
    employee_number: str,
    biodata: dict,
) -> None:
    """Insert an employee row. Caller owns commit."""
    db.execute(
        text("""
            INSERT INTO employee (
                employee_id, workspace_id, full_name,
                employee_number, personal_details_encrypted, status
            )
            VALUES (
                CAST(:eid AS uuid), :wid, :name,
                :emp_number, :biodata, 'ACTIVE'
            )
        """),
        {
            "eid":        employee_id,
            "wid":        workspace_id,
            "name":       full_name,
            "emp_number": employee_number,
            "biodata":    Json(biodata),
        },
    )


def insert_employee_contract(
    db,
    employee_id: str,
    salary_definition_id: str | None,
    start_date: date | None = None,
    grade_id: str | None = None,
    designation_id: str | None = None,
    shift_type: str | None = None,
    state_of_tax: str | None = None,
    skill_level: str | None = None,
    is_union_member: bool = False,
    change_reason: str | None = None,
    end_date: date | None = None,
    close_current: bool = False,
    imported_grade_label: str | None = None,
    imported_designation_label: str | None = None,
) -> str:
    """Insert a new contract row. Returns the new contract_id.

    start_date defaults to CURRENT_DATE when None (onboarding path).
    end_date is NULL unless explicitly supplied (onboarding may set contract_end).

    When close_current=True the current open contract is closed with
    end_date = start_date - 1 day before the new row is written.
    This preserves the uq_employee_active_contract partial unique index
    (at most one NULL end_date per employee).
    """
    if close_current:
        if start_date is None:
            raise ValueError("start_date must be provided when close_current=True")
        db.execute(
            text("""
                UPDATE employee_contract
                SET    end_date = CAST(:new_start AS DATE) - INTERVAL '1 day'
                WHERE  employee_id = CAST(:eid AS uuid)
                  AND  end_date IS NULL
            """),
            {"eid": employee_id, "new_start": str(start_date)},
        )

    contract_id = str(uuid4())
    db.execute(
        text("""
            INSERT INTO employee_contract (
                contract_id, employee_id, salary_definition_id,
                grade_id, designation_id, start_date, end_date,
                shift_type, state_of_tax, skill_level, is_union_member,
                change_reason, imported_grade_label, imported_designation_label
            )
            VALUES (
                CAST(:cid AS uuid), CAST(:eid AS uuid), CAST(:sd_id AS uuid),
                CAST(:grade_id AS uuid), CAST(:designation_id AS uuid),
                COALESCE(CAST(:start_date AS DATE), CURRENT_DATE),
                CAST(:end_date AS DATE),
                :shift_type, :state_of_tax, :skill_level, :is_union_member,
                :change_reason, :imported_grade_label, :imported_designation_label
            )
        """),
        {
            "cid":                       contract_id,
            "eid":                       employee_id,
            "sd_id":                     salary_definition_id,
            "grade_id":                  grade_id,
            "designation_id":            designation_id,
            "start_date":                str(start_date) if start_date else None,
            "end_date":                  str(end_date) if end_date else None,
            "shift_type":                shift_type,
            "state_of_tax":              state_of_tax,
            "skill_level":               skill_level,
            "is_union_member":           is_union_member,
            "change_reason":             change_reason,
            "imported_grade_label":      imported_grade_label,
            "imported_designation_label": imported_designation_label,
        },
    )
    return contract_id


def enroll_employee_contract(
    db,
    employee_id: str,
    salary_definition_id: str,
    grade_id: str | None = None,
    designation_id: str | None = None,
) -> bool:
    """Set salary_definition_id (and optionally grade/designation) on the open unenrolled contract.

    Returns True if a row was updated. The contract must have salary_definition_id IS NULL.
    Caller owns commit.
    """
    result = db.execute(
        text("""
            UPDATE employee_contract
            SET    salary_definition_id = CAST(:sd_id AS uuid),
                   grade_id       = COALESCE(CAST(:grade_id AS uuid), grade_id),
                   designation_id = COALESCE(CAST(:designation_id AS uuid), designation_id)
            WHERE  employee_id = CAST(:eid AS uuid)
              AND  (end_date IS NULL OR end_date >= CURRENT_DATE)
              AND  salary_definition_id IS NULL
        """),
        {
            "eid":            employee_id,
            "sd_id":          salary_definition_id,
            "grade_id":       grade_id,
            "designation_id": designation_id,
        },
    )
    return result.rowcount > 0


def bulk_enroll_employee_contracts(
    db,
    workspace_id: str,
    employee_ids: list[str],
    salary_definition_id: str,
    grade_id: str | None = None,
    designation_id: str | None = None,
) -> dict:
    """Bulk-enroll not-enrolled employees. Returns {enrolled, skipped, failed, details}.

    Workspace guard fires first — employee_ids not belonging to this workspace are failed.
    Already-enrolled employees are skipped (not an error).
    Caller owns commit.
    """
    valid_rows = db.execute(
        text("""
            SELECT CAST(employee_id AS text)
            FROM employee
            WHERE employee_id = ANY(CAST(:ids AS uuid[]))
              AND workspace_id = :wid
        """),
        {"ids": employee_ids, "wid": workspace_id},
    ).fetchall()
    valid_ids = {row[0] for row in valid_rows}
    failed_ids = set(employee_ids) - valid_ids

    if not valid_ids:
        return {
            "enrolled": 0,
            "skipped": 0,
            "failed": len(failed_ids),
            "details": [{"employee_id": i, "status": "failed", "reason": "not found"} for i in failed_ids],
        }

    already_rows = db.execute(
        text("""
            SELECT CAST(ec.employee_id AS text)
            FROM employee_contract ec
            JOIN employee e ON e.employee_id = ec.employee_id AND e.workspace_id = :wid
            WHERE ec.employee_id = ANY(CAST(:ids AS uuid[]))
              AND (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
              AND ec.salary_definition_id IS NOT NULL
        """),
        {"ids": list(valid_ids), "wid": workspace_id},
    ).fetchall()
    skipped_ids = {row[0] for row in already_rows}

    to_enroll = list(valid_ids - skipped_ids)
    enrolled_ids: set[str] = set()
    if to_enroll:
        updated_rows = db.execute(
            text("""
                UPDATE employee_contract ec
                SET    salary_definition_id = CAST(:sd_id AS uuid),
                       grade_id       = COALESCE(CAST(:grade_id AS uuid), ec.grade_id),
                       designation_id = COALESCE(CAST(:designation_id AS uuid), ec.designation_id)
                FROM   employee e
                WHERE  ec.employee_id = e.employee_id
                  AND  e.workspace_id = :wid
                  AND  ec.employee_id = ANY(CAST(:ids AS uuid[]))
                  AND  (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
                  AND  ec.salary_definition_id IS NULL
                RETURNING CAST(ec.employee_id AS text)
            """),
            {
                "sd_id":          salary_definition_id,
                "grade_id":       grade_id,
                "designation_id": designation_id,
                "ids":            to_enroll,
                "wid":            workspace_id,
            },
        ).fetchall()
        enrolled_ids = {row[0] for row in updated_rows}
        failed_ids |= set(to_enroll) - enrolled_ids

    details = (
        [{"employee_id": i, "status": "enrolled"} for i in enrolled_ids]
        + [{"employee_id": i, "status": "skipped"} for i in skipped_ids]
        + [{"employee_id": i, "status": "failed", "reason": "no open unenrolled contract or not found"} for i in failed_ids]
    )
    return {
        "enrolled": len(enrolled_ids),
        "skipped":  len(skipped_ids),
        "failed":   len(failed_ids),
        "details":  details,
    }


def update_employee(
    db,
    workspace_id: str,
    employee_id: str,
    full_name: str | None = None,
    status: str | None = None,
) -> bool:
    """Update mutable employee fields. Returns True if a row was updated."""
    if full_name is None and status is None:
        return False

    sets = []
    params: dict = {"wid": workspace_id, "eid": employee_id}
    if full_name is not None:
        sets.append("full_name = :full_name")
        params["full_name"] = full_name
    if status is not None:
        sets.append("status = :status")
        params["status"] = status

    result = db.execute(
        text(f"UPDATE employee SET {', '.join(sets)} WHERE workspace_id = :wid AND employee_id = CAST(:eid AS uuid)"),  # noqa: S608
        params,
    )
    return result.rowcount > 0


def update_employee_contract(
    db,
    workspace_id: str,
    contract_id: str,
    end_date: date | None,
    change_reason: str | None,
) -> bool:
    """Update contract end_date and/or change_reason. Returns True if updated.

    Workspace-scoped via the employee FK — employee_contract has no workspace_id.
    """
    sets = []
    params: dict = {"cid": contract_id, "wid": workspace_id}
    if end_date is not None:
        sets.append("end_date = CAST(:end_date AS DATE)")
        params["end_date"] = str(end_date)
    if change_reason is not None:
        sets.append("change_reason = :change_reason")
        params["change_reason"] = change_reason

    if not sets:
        return False

    # PostgreSQL UPDATE ... FROM: SET clause must use bare column names, not aliases.
    result = db.execute(
        text(f"""
            UPDATE employee_contract
            SET    {', '.join(sets)}
            FROM   employee e
            WHERE  employee_contract.contract_id = CAST(:cid AS uuid)
              AND  employee_contract.employee_id = e.employee_id
              AND  e.workspace_id                = :wid
        """),
        params,
    )
    return result.rowcount > 0


# ---------------------------------------------------------------------------
# Private serialisers
# ---------------------------------------------------------------------------

def _employee_row_to_dict(r) -> dict:
    return {
        "employee_id":            str(r[0]),
        "employee_number":        r[1],
        "full_name":              r[2],
        "status":                 r[3],
        "created_at":             r[4].isoformat() if r[4] else None,
        "contract_id":            str(r[5]) if r[5] else None,
        "salary_definition_id":   str(r[6]) if r[6] else None,
        "salary_definition_code": r[7],
        "grade_id":               str(r[8]) if r[8] else None,
        "grade_code":             r[9],
        "designation_id":         str(r[10]) if r[10] else None,
        "designation_code":       r[11],
        "contract_start":         r[12].isoformat() if r[12] else None,
        "contract_end":           r[13].isoformat() if r[13] else None,
        "shift_type":             r[14],
        "state_of_tax":           r[15],
        "skill_level":            r[16],
        "is_union_member":              r[17],
        "change_reason":               r[18],
        "imported_grade_label":        r[19],
        "imported_designation_label":  r[20],
    }


def _contract_row_to_dict(r) -> dict:
    return {
        "contract_id":            str(r[0]),
        "salary_definition_id":   str(r[1]) if r[1] else None,
        "salary_definition_code": r[2],
        "grade_id":               str(r[3]) if r[3] else None,
        "grade_code":             r[4],
        "designation_id":         str(r[5]) if r[5] else None,
        "designation_code":       r[6],
        "start_date":             r[7].isoformat() if r[7] else None,
        "end_date":               r[8].isoformat() if r[8] else None,
        "shift_type":             r[9],
        "state_of_tax":           r[10],
        "skill_level":            r[11],
        "is_union_member":        r[12],
        "change_reason":          r[13],
    }
