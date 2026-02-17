from sqlalchemy import text
from psycopg2.extras import Json
from backend.infra.db.session import SessionLocal


def save_event(event: dict):
    db = SessionLocal()

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
            "payload": Json(event["event_payload"]),
        }
    )

    db.commit()
    db.close()

