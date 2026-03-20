import uuid
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from backend.infra.db.session import Base


class StatutoryRule(Base):
    __tablename__ = "statutory_rule"

    statutory_rule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state = Column(String(50), nullable=False)
    version = Column(Integer, nullable=False)
    rules_jsonb = Column(JSONB, nullable=False)
    tax_method = Column(String(30), nullable=False, default="CUMULATIVE")
    country_code = Column(String(10), nullable=True)
