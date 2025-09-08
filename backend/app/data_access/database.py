"""Handles database interactions."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# In backend/assets.db
SQLITE_DATABASE_URL = "sqlite:///./assets.db"

engine = create_engine(
    SQLITE_DATABASE_URL, connect_args={"check_same_thread": False} # Required by SQLite for FastAPI async operations
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
