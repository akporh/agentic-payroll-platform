import uuid
from sqlalchemy import Column, String, Date
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ
from backend.infra.db.session import Base


class NationalPublicHoliday(Base):
    __tablename__ = "national_public_holiday"

    holiday_id   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_code = Column(String(10),  nullable=False)
    holiday_date = Column(Date,        nullable=False)
    name         = Column(String(255), nullable=False)
    created_at   = Column(TIMESTAMPTZ, nullable=False)
