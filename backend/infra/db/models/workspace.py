import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from backend.infra.db.session import Base


class Workspace(Base):
    __tablename__ = "workspace"

    workspace_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("account.account_id"))
    name = Column(String(255), nullable=False)
    country_code = Column(String(10))
    base_currency = Column(String(10))
    status = Column(String(50), nullable=False)