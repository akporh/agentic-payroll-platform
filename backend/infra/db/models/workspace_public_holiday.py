import uuid
from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ
from backend.infra.db.session import Base


class WorkspacePublicHoliday(Base):
    __tablename__ = "workspace_public_holiday"

    holiday_id   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.workspace_id"), nullable=False)
    holiday_date = Column(Date,        nullable=False)
    name         = Column(String(255), nullable=False)
    created_at   = Column(TIMESTAMPTZ, nullable=False)
