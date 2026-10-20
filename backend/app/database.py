"""
Database layer using SQLAlchemy.
Designed for SQLite in local dev with seamless upgrade to PostgreSQL.
"""
import os
import json
from datetime import datetime
from typing import Generator
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

DATABASE_URL = os.getenv("DATABASE_URL")

# Fall back to local SQLite only when DATABASE_URL is unset or empty
if not DATABASE_URL or not DATABASE_URL.strip():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DEFAULT_DB_PATH = os.path.join(BASE_DIR, "agentic_dating.db").replace("\\", "/")
    DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH}"
elif DATABASE_URL.startswith("postgres://"):
    # Fix Render / Neon legacy postgres:// scheme for SQLAlchemy compatibility
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs connect_args check_same_thread=False
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class ProfileDB(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), nullable=False, index=True)
    age = Column(Integer, nullable=True)
    occupation = Column(String(160), nullable=True)
    location = Column(String(120), nullable=True)
    source = Column(String(40), nullable=False, default="self-reported")  # "self-reported" or "synthetic"
    raw_input = Column(Text, nullable=False)
    avatar_url = Column(String(400), nullable=True)
    analysis_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    dates_as_a = relationship("DateSimulationDB", foreign_keys="DateSimulationDB.profile_a_id", cascade="all, delete-orphan")
    dates_as_b = relationship("DateSimulationDB", foreign_keys="DateSimulationDB.profile_b_id", cascade="all, delete-orphan")

    def get_analysis_dict(self) -> dict:
        try:
            return json.loads(self.analysis_json)
        except Exception:
            return {}


class DateSimulationDB(Base):
    __tablename__ = "date_simulations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_a_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_b_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    compatibility_score = Column(Integer, nullable=False)
    summary_rationale = Column(Text, nullable=False)
    transcript_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_profiles_pair", "profile_a_id", "profile_b_id"),
    )

    def get_transcript_dict(self) -> dict:
        try:
            return json.loads(self.transcript_json)
        except Exception:
            return {}


def init_db():
    """Create all tables if they don't exist yet."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
