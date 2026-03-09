import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from backend.infra.db.session import Base


class PayrollRule(Base):
    __tablename__ = "payroll_rule"

    rule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.workspace_id"))
    rule_name = Column(String(255), nullable=False)
    rule_definition_json = Column(JSONB, nullable=False)
    rule_type = Column(String(100))
    is_active = Column(Boolean, default=True)