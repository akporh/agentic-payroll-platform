import uuid
from sqlalchemy import Column, Numeric, String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from backend.infra.db.session import Base


class PayrollReconciliation(Base):
    __tablename__ = "payroll_reconciliation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payroll_run_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payroll_run.payroll_run_id"),
        nullable=False,
        unique=True,
    )
    expected_total = Column(Numeric(18, 2), nullable=False)
    actual_total = Column(Numeric(18, 2), nullable=True)
    status = Column(String(20), nullable=False)
    reconciled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    notes = Column(Text, nullable=True)
    resolved_by = Column(String(255), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
