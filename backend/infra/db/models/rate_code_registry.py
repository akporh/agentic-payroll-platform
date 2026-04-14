import uuid
from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ
from backend.infra.db.session import Base


class RateCodeRegistry(Base):
    __tablename__ = "rate_code_registry"

    rate_code_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.workspace_id"), nullable=True)
    code         = Column(String(50),  nullable=False)
    multiplier   = Column(Numeric(8, 4), nullable=False)
    unit         = Column(String(20),  nullable=False)
    base         = Column(String(50),  nullable=False)
    description  = Column(String(255), nullable=False)
    is_active    = Column(Boolean,     nullable=False, default=True)
    created_at   = Column(TIMESTAMPTZ, nullable=False)
