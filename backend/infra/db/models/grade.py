import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from backend.infra.db.session import Base


class Grade(Base):
    __tablename__ = "grade"

    grade_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.workspace_id"), nullable=False)
    grade_code = Column(String(50), nullable=False)
    description = Column(String(255))