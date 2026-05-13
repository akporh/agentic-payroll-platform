import uuid
import enum
from sqlalchemy import Column, Date, Text, Enum, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from backend.infra.db.session import Base

_TS = DateTime(timezone=True)


class DerivationStatus(str, enum.Enum):
    PENDING  = "PENDING"
    DERIVED  = "DERIVED"
    APPROVED = "APPROVED"
    FAILED   = "FAILED"


class TimesheetEntry(Base):
    __tablename__ = "timesheet_entry"

    timesheet_entry_id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id             = Column(UUID(as_uuid=True), ForeignKey("workspace.workspace_id"), nullable=False)
    employee_id              = Column(UUID(as_uuid=True), ForeignKey("employee.employee_id"), nullable=False)
    period_start             = Column(Date, nullable=False)
    period_end               = Column(Date, nullable=False)
    attendance_grid_jsonb    = Column(JSONB, nullable=False)
    derivation_status        = Column(Enum(DerivationStatus, name="derivation_status"), nullable=False, default=DerivationStatus.PENDING)
    derivation_error         = Column(Text)
    policy_snapshot_jsonb    = Column(JSONB)
    derivation_summary_jsonb = Column(JSONB)
    created_at               = Column(_TS, nullable=False, server_default=func.now())
    updated_at               = Column(_TS, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("workspace_id", "employee_id", "period_start", name="uq_timesheet_entry_workspace_employee_period"),
    )
