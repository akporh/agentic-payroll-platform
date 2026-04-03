import uuid
from sqlalchemy import Column, Date, ForeignKey
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from backend.infra.db.session import Base


class RuleSet(Base):
    """Immutable versioned rule set for a workspace.

    Rows are never updated after creation. Corrections are published as new
    rows (same or different effective_from). The selection query uses
    ORDER BY effective_from DESC, created_at DESC to pick the most recently
    published rule set effective on or before a given date.
    """
    __tablename__ = "rule_set"

    rule_set_id    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id   = Column(UUID(as_uuid=True), ForeignKey("workspace.workspace_id"), nullable=False)
    effective_from = Column(Date, nullable=False)
    created_at     = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_by     = Column(UUID(as_uuid=True), nullable=False)
