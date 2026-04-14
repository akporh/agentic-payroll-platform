import uuid
from sqlalchemy import Column, String, Integer, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from backend.infra.db.session import Base


class StatutoryRule(Base):
    __tablename__ = "statutory_rule"
    __table_args__ = (
        UniqueConstraint("country_code", "effective_from", name="uq_statutory_rule_country_effective"),
    )

    statutory_rule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state = Column(String(50), nullable=False)
    version = Column(Integer, nullable=False)
    rules_jsonb = Column(JSONB, nullable=False)
    tax_method = Column(String(30), nullable=False, default="CUMULATIVE")
    country_code = Column(String(10), nullable=True)
    # Date from which this statutory rule takes effect.
    # Existing rows are backfilled to 2000-01-01 by migration a8b9c0d1e2f3.
    # All new statutory rules must have an explicit effective_from before
    # state transitions to 'LIVE'.
    effective_from = Column(Date, nullable=False, server_default="2000-01-01")
