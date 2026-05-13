import uuid
from sqlalchemy import Column, String, Date, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ
from backend.infra.db.session import Base


class WorkspacePayrollConfig(Base):
    __tablename__ = "workspace_payroll_config"

    config_id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id          = Column(UUID(as_uuid=True), ForeignKey("workspace.workspace_id"), nullable=False)
    effective_from        = Column(Date, nullable=False)
    ph_mode               = Column(String(50),  nullable=False, default="FILE_BASED")
    ph_rate_code          = Column(String(20),  nullable=False, default="OT005")
    saturday_ph_rule      = Column(String(50),  nullable=False, default="PH_TAKES_PRECEDENCE")
    sunday_ph_rule        = Column(String(50),  nullable=False, default="PH_TAKES_PRECEDENCE")
    d3_leave_overlap_rule = Column(String(50),  nullable=False, default="LEAVE_ABSORBS_PH")
    d4_absence_rule       = Column(String(50),  nullable=False, default="ABSENT_IS_DEDUCTIBLE")
    timesheet_enabled     = Column(Boolean,     nullable=False, server_default="false")
    updated_at            = Column(TIMESTAMPTZ, nullable=False)
    updated_by            = Column(UUID(as_uuid=True))
