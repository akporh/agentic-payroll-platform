"""
Audit Log Repository.

Responsible for persisting audit trail records.
Handles JSON sanitization at infrastructure boundary.
"""

from sqlalchemy import text
from psycopg2.extras import Json
from backend.infra.db.session import SessionLocal
import json


def _sanitize_json(payload: dict | None) -> dict | None:
    """
    Convert non-JSON-serializable types (Decimal, UUID, etc.)
    into safe representations using default=str.
    """
    if payload is None:
        return None

    return json.loads(json.dumps(payload, default=str))


def save_audit_log(workspace_id: str, audit: dict):
    """
    Persist an audit log entry.

    Infrastructure responsibility:
    - Sanitize JSON fields
    - Execute insert
    - Commit transaction
    """

    db = SessionLocal()

    safe_old_value = _sanitize_json(audit.get("old_value_jsonb"))
    safe_new_value = _sanitize_json(audit.get("new_value_jsonb"))

    db.execute(
        text("""
        INSERT INTO audit_log (
            audit_log_id,
            workspace_id,
            entity_type,
            entity_id,
            action,
            old_value_jsonb,
            new_value_jsonb,
            performed_by
        )
        VALUES (
            gen_random_uuid(),
            :workspace_id,
            :entity_type,
            :entity_id,
            :action,
            :old_value,
            :new_value,
            :performed_by
        )
        """),
        {
            "workspace_id": workspace_id,
            "entity_type": audit["entity_type"],
            "entity_id": audit["entity_id"],
            "action": audit["action"],
            "old_value": Json(safe_old_value) if safe_old_value is not None else None,
            "new_value": Json(safe_new_value) if safe_new_value is not None else None,
            "performed_by": audit["performed_by"],
        }
    )

    db.commit()
    db.close()