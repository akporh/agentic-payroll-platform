from sqlalchemy import text
from psycopg2.extras import Json
from backend.infra.db.session import SessionLocal
import json


def save_event(event: dict):
    db = SessionLocal()

    safe_payload = json.loads(
        json.dumps(event["event_payload"], default=str)
    )

    db.execute(
        text("""
        INSERT INTO event_store (
            event_id,
            aggregate_type,
            aggregate_id,
            event_type,
            event_payload
        )
        VALUES (
            gen_random_uuid(),
            :aggregate_type,
            :aggregate_id,
            :event_type,
            :payload
        )
        """),
        {
            "aggregate_type": event["aggregate_type"],
            "aggregate_id": event["aggregate_id"],
            "event_type": event["event_type"],
            "payload": Json(safe_payload),
        }
    )

    db.commit()
    db.close()