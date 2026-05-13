import uuid
from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey, DateTime
from sqlalchemy.sql import func
from backend.infra.db.session import Base

_TS = DateTime(timezone=True)


class PlatformAttendanceTemplateVersion(Base):
    __tablename__ = "platform_attendance_template_version"

    version_tag = Column(String(10), primary_key=True)
    released_at = Column(_TS, nullable=False, server_default=func.now())
    notes       = Column(String(500))


class PlatformAttendanceCodeTemplate(Base):
    __tablename__ = "platform_attendance_code_template"

    client_code           = Column(String(20), primary_key=True)
    description           = Column(String(200))
    category              = Column(String(10), nullable=False)
    is_active             = Column(Boolean, nullable=False, default=True)
    introduced_in_version = Column(String(10), ForeignKey("platform_attendance_template_version.version_tag"), nullable=False)
    created_at            = Column(_TS, nullable=False, server_default=func.now())


class PlatformAttendancePolicyTemplate(Base):
    __tablename__ = "platform_attendance_policy_template"

    client_code                  = Column(String(20), ForeignKey("platform_attendance_code_template.client_code"), primary_key=True)
    counts_as_paid               = Column(Boolean, nullable=False, default=True)
    counts_towards_ot_threshold  = Column(Boolean, nullable=False, default=True)
    hours_equivalent             = Column(Numeric(5, 2))
    unit_fraction                = Column(Numeric(5, 4))
    eligible_for_shift_allowance = Column(Boolean, nullable=False, default=False)
    eligible_for_ot              = Column(Boolean, nullable=False, default=False)
    introduced_in_version        = Column(String(10), ForeignKey("platform_attendance_template_version.version_tag"), nullable=False)
    created_at                   = Column(_TS, nullable=False, server_default=func.now())
