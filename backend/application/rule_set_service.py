"""Auto-publish rule_set snapshots after every payroll_rule create/version-save.

Caller is responsible for db.commit() after this returns.
If this raises RuleSetLockedError, the caller should translate it to HTTP 409.
"""
import json
import uuid
import logging
from datetime import date

from sqlalchemy import text

_log = logging.getLogger(__name__)

SYSTEM_ACTOR = "00000000-0000-0000-0000-000000000000"


class RuleSetLockedError(Exception):
    """Rule set for the given date is referenced by a payroll_run and cannot be replaced."""


def auto_publish(db, workspace_id: str, effective_from: date, created_by_uuid: str | None = None) -> str:
    """Snapshot all active payroll_rule rows for workspace into a rule_set.

    Steps:
      1. Check if rule_set exists for (workspace_id, effective_from).
         a. Not found   → create new rule_set row.
         b. Found, not referenced by any payroll_run → DELETE+INSERT items.
         c. Found, referenced by a payroll_run → raise RuleSetLockedError.
      2. SELECT DISTINCT ON (rule_name) — latest active version per rule up to effective_from.
      3. INSERT selected rules as rule_set_items.

    Returns the rule_set_id.
    Raises RuleSetLockedError if the rule_set for this date is locked by a payroll_run.
    Does NOT commit — caller is responsible for db.commit().
    """
    actor = created_by_uuid or SYSTEM_ACTOR
    eff_str = str(effective_from)

    # Step 1: lookup existing rule_set
    existing = db.execute(
        text("""
            SELECT rs.rule_set_id,
                   EXISTS(
                       SELECT 1 FROM payroll_run pr
                       WHERE pr.rule_set_id = rs.rule_set_id
                   ) AS is_locked
            FROM rule_set rs
            WHERE rs.workspace_id = :wid AND rs.effective_from = :eff
        """),
        {"wid": workspace_id, "eff": eff_str},
    ).fetchone()

    if existing is None:
        # 1a — create new rule_set
        rule_set_id = str(uuid.uuid4())
        db.execute(
            text("""
                INSERT INTO rule_set (rule_set_id, workspace_id, effective_from, created_by)
                VALUES (:id, :wid, :eff, :by)
            """),
            {"id": rule_set_id, "wid": workspace_id, "eff": eff_str, "by": actor},
        )
    else:
        rule_set_id = str(existing[0])
        is_locked = existing[1]

        if is_locked:
            # 1c — locked: a payroll_run references this rule_set; reject
            raise RuleSetLockedError(
                f"A locked rule set already exists for {eff_str}. "
                "Choose a different effective date."
            )

        # 1b — unlocked: wipe existing items and re-insert
        db.execute(
            text("DELETE FROM rule_set_item WHERE rule_set_id = :id"),
            {"id": rule_set_id},
        )

    # Step 2: DISTINCT ON — latest active version per rule_name up to effective_from
    rule_rows = db.execute(
        text("""
            SELECT DISTINCT ON (rule_name)
                rule_name, rule_definition_json, rule_type
            FROM payroll_rule
            WHERE workspace_id = :wid
              AND is_active = TRUE
              AND effective_from <= :eff
            ORDER BY rule_name, effective_from DESC
        """),
        {"wid": workspace_id, "eff": eff_str},
    ).fetchall()

    # Step 3: insert rule_set_items
    for row in rule_rows:
        rule_name, rule_def, rule_type = row[0], row[1], row[2]
        db.execute(
            text("""
                INSERT INTO rule_set_item (rule_set_id, rule_name, rule_definition_json, rule_type)
                VALUES (:rs_id, :name, CAST(:def AS jsonb), :rtype)
            """),
            {
                "rs_id": str(rule_set_id),
                "name": rule_name,
                "def": json.dumps(rule_def) if isinstance(rule_def, dict) else rule_def,
                "rtype": rule_type,
            },
        )

    _log.info(
        "auto_publish: rule_set %s for workspace %s effective %s — %d rules snapshotted",
        rule_set_id, workspace_id, eff_str, len(rule_rows),
    )
    return str(rule_set_id)
