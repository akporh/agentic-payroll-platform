import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.infra.db.session import Base


class PayCycle(Base):
    __tablename__ = "pay_cycle"

    pay_cycle_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.workspace_id"), nullable=False)

    frequency = Column(String(20), nullable=False)
    run_day = Column(Integer, nullable=False)
    cutoff_day = Column(Integer, nullable=False)
    payment_day = Column(Integer, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    definition_json = Column(JSONB, nullable=True)