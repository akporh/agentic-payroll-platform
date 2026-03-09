import uuid
from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from backend.infra.db.session import Base


class SalaryDefinition(Base):
    __tablename__ = "salary_definition"

    salary_definition_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.workspace_id"))
    name = Column(String(255))
    components_jsonb = Column(JSONB, nullable=False)
    effective_from = Column(Date)
    effective_to = Column(Date)
    