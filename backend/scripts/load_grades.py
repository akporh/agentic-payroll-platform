import json
import uuid
from backend.infra.db import get_session
from sqlalchemy import text


def load_grades(workspace_id: str, path: str):
    with open(path) as f:
        grades = json.load(f)

    db = get_session()

    for g in grades:
        db.execute(
            text("""
            INSERT INTO grade (grade_id, workspace_id, grade_code, description)
            VALUES (:id, :ws, :code, :desc)
            """),
            {
                "id": str(uuid.uuid4()),
                "ws": workspace_id,
                "code": g["grade_code"],
                "desc": g.get("description"),
            },
        )

    db.commit()
    print("Loaded grades successfully.")


if __name__ == "__main__":
    load_grades(
        workspace_id="6b70612c-b2e1-4275-800c-33140e7f4ebd",
        path="data/acme_grades.json",
    )
