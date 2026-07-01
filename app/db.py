"""SQLite persistence layer using SQLAlchemy."""
 
from __future__ import annotations
 
import os
from contextlib import contextmanager
from datetime import datetime
 
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
 
DB_PATH = os.environ.get("RESUME_DB_PATH", "resumes.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"
 
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
 
Base = declarative_base()
 
 
class Candidate(Base):
    __tablename__ = "candidates"
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(64), nullable=True)
    location = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    total_experience_years = Column(Float, nullable=True)
 
    # Stored as JSON strings to keep the schema simple (SQLite has no native JSON column pre-3.9 bindings here)
    skills_json = Column(Text, nullable=False, default="[]")
    education_json = Column(Text, nullable=False, default="[]")
    experience_json = Column(Text, nullable=False, default="[]")
 
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
 
 
def init_db() -> None:
    Base.metadata.create_all(bind=engine)
 
 
@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
 