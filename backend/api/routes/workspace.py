from fastapi import APIRouter
from sqlalchemy import text
from backend.infra.db.session import SessionLocal

router = APIRouter()


@router.get("/workspace/info")
def workspace_info():
    db = SessionLocal()

    workspace = db.execute(
        text("SELECT workspace_id, name FROM workspace LIMIT 1")
    ).fetchone()

    if not workspace:
        db.close()
        return {"workspace_name": "Not Found", "active_employee_count": 0}

    workspace_id = workspace[0]
    workspace_name = workspace[1]

    count = db.execute(
        text("""
            SELECT COUNT(*)
            FROM employee
            WHERE workspace_id = :wid
              AND status = 'ACTIVE'
        """),
        {"wid": workspace_id}
    ).scalar()

    db.close()

    return {
        "workspace_id": str(workspace_id),
        "workspace_name": workspace_name,
        "active_employee_count": count
    }
