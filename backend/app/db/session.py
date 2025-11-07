"""
Database session management and connection.
"""
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from ..core.config import get_settings
from .models import Base


settings = get_settings()

# Create engine with appropriate settings
# For SQLite, use check_same_thread=False to allow FastAPI's thread pool
connect_args = {}
poolclass = None

if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    # Use StaticPool for SQLite to avoid connection issues
    poolclass = StaticPool

engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args=connect_args,
    poolclass=poolclass,
)


# Enable foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints for SQLite."""
    if settings.database_url.startswith("sqlite"):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_database() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Yields:
        Database session that will be automatically closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
