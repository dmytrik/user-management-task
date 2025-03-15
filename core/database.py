from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from core.settings import settings


engine = create_engine(settings.database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


def get_db():
    """Provide a database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
