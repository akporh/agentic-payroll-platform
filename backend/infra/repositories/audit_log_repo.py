from sqlalchemy import text
from psycopg2.extras import Json
from backend.infra.db.session import SessionLocal


def save_audit_log(workspace_id: str, audit: dict):
    db = SessionLocal()

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
            "old_value": Json(audit.get("old_value_jsonb")),
            "new_value": Json(audit.get("new_value_jsonb")),
            "performed_by": audit["performed_by"],
        }
    )

    db.commit()
    db.close()

