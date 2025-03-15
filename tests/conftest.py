import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.settings import settings
from core.database import Base
from run import create_app


settings.environment = "testing"
TEST_DATABASE_URL = settings.database_url
test_engine = create_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


@pytest.fixture(scope="function")
def test_app(monkeypatch):
    """Create and configure a Flask app instance for testing."""
    monkeypatch.setattr("core.database.engine", test_engine)
    monkeypatch.setattr("core.database.SessionLocal", TestSessionLocal)

    app = create_app()
    app.config.update({"TESTING": True})

    Base.metadata.create_all(bind=test_engine)
    yield app
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def test_client(test_app):
    """Provide a test client for the Flask app."""
    return test_app.test_client()


@pytest.fixture(scope="function")
def db_session(monkeypatch):
    """Provide a test database session with cleanup."""
    session = TestSessionLocal()

    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()

    def override_get_db():
        """Override the get_db dependency for testing."""
        yield session

    monkeypatch.setattr("core.database.get_db", override_get_db)

    yield session

    session.rollback()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()
