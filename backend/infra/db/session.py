import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base



DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg2://michaelemedo@localhost:5432/payroll_dev")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()