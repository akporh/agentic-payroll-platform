import uuid
from sqlalchemy import Column, Integer, Boolean, Date, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from backend.infra.db.session import Base


class ComponentMetadata(Base):
    __tablename__ = "component_metadata"

    component_metadata_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_code = Column(String(10), nullable=False)
    version = Column(Integer, nullable=False)
    rules_jsonb = Column(JSONB, nullable=False)
    effective_from = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)