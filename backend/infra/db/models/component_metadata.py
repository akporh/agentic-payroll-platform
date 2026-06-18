import uuid
from sqlalchemy import Column, Integer, Boolean, Date, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from backend.infra.db.session import Base


class ComponentMetadata(Base):
    __tablename__ = "component_metadata"

    component_metadata_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    component_code = Column(Text, nullable=False)
    country_code = Column(String(10), nullable=False)
    version = Column(Integer, nullable=False)
    metadata_json = Column(JSONB, nullable=False)
    effective_from = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    component_class = Column(Text, nullable=True)
    calculation_method = Column(Text, nullable=True)
    execution_priority = Column(Integer, nullable=True)


class ClientComponentMetadata(Base):
    __tablename__ = "client_component_metadata"

    client_component_metadata_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False)
    component_code = Column(Text, nullable=False)
    overrides_json = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True, nullable=True)
    proration_strategy = Column(Text, nullable=True)