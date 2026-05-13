import uuid
from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.infra.db.session import Base

_TS = DateTime(timezone=True)


class AttendanceCodeConfig(Base):
    __tablename__ = "attendance_code_config"

    attendance_code_config_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id              = Column(UUID(as_uuid=True), ForeignKey("workspace.workspace_id"), nullable=False)
    client_code               = Column(String(20), nullable=False)
    description               = Column(String(200))
    category                  = Column(String(10), nullable=False)
    is_active                 = Column(Boolean, nullable=False, default=True)
    created_at                = Column(_TS, nullable=False, server_default=func.now())
    updated_at                = Column(_TS, nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("workspace_id", "client_code", name="uq_attendance_code_config_workspace_code"),)


class AttendancePolicyConfig(Base):
    __tablename__ = "attendance_policy_config"

    attendance_policy_config_id  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id                 = Column(UUID(as_uuid=True), ForeignKey("workspace.workspace_id"), nullable=False)
    client_code                  = Column(String(20), nullable=False)
    counts_as_paid               = Column(Boolean, nullable=False, default=True)
    counts_towards_ot_threshold  = Column(Boolean, nullable=False, default=True)
    hours_equivalent             = Column(Numeric(5, 2))
    unit_fraction                = Column(Numeric(5, 4))
    eligible_for_shift_allowance = Column(Boolean, nullable=False, default=False)
    eligible_for_ot              = Column(Boolean, nullable=False, default=False)
    created_at                   = Column(_TS, nullable=False, server_default=func.now())
    updated_at                   = Column(_TS, nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("workspace_id", "client_code", name="uq_attendance_policy_config_workspace_code"),)
