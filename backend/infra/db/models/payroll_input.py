"""
PayrollInput ORM model — canonical per-period event input layer.

Rows are inserted with payroll_run_id = NULL (unclaimed).  During a payroll
run, link_inputs_to_run() claims all unclaimed rows for the workspace by
setting payroll_run_id, making them available to the calculation chain.
"""

import uuid
from sqlalchemy import Column, Numeric, String, DateTime, Date, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from backend.infra.db.session import Base



class PayrollInput(Base):
    __tablename__ = "payroll_input"

    payroll_input_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspace.workspace_id"),
        nullable=False,
    )
    payroll_run_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payroll_run.payroll_run_id"),
        nullable=True,
    )
    employee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("employee.employee_id"),
        nullable=False,
    )
    input_code = Column(String(50), nullable=False)
    input_category = Column(String(30), nullable=False)
    quantity = Column(Numeric(12, 2), nullable=True)
    reference_date = Column(Date, nullable=True)
    source = Column(String(50), server_default="MANUAL")
    input_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
