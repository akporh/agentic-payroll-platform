import uuid
from sqlalchemy import Column, String, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from backend.infra.db.session import Base


class Grade(Base):
    __tablename__ = "grade"

    grade_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.workspace_id"), nullable=False)
    grade_code = Column(String(50), nullable=False)
    description = Column(String(255))
    # Percentage salary structure (O2). When total_monthly is set, the engine derives
    # BASIC/HOUSING/TRANSPORT/UTILITY from total_monthly × pct instead of reading
    # salary_definition.components_jsonb amounts. All four pct columns must be set together.
    total_monthly = Column(Numeric(15, 2), nullable=True)
    basic_pct = Column(Numeric(5, 4), nullable=True)
    housing_pct = Column(Numeric(5, 4), nullable=True)
    transport_pct = Column(Numeric(5, 4), nullable=True)
    utility_pct = Column(Numeric(5, 4), nullable=True)