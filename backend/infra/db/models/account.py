import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from backend.infra.db.session import Base


class Account(Base):
    __tablename__ = "account"

    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
