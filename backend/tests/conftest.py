"""Shared pytest fixtures.

Provides two flavours of fixture:

* ``client`` — a FastAPI ``TestClient`` for pure-unit endpoint tests (no DB).
* ``db_session`` — a transactional SQLAlchemy session backed by a real
  Postgres (with pgvector). Integration tests using it are skipped
  automatically when no database is reachable, so the unit suite still runs
  anywhere.
"""

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401  (register models on Base.metadata)
from app.core.database import Base, get_db
from app.main import create_app

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://salon:salon@localhost:5432/salon",
)


@pytest.fixture
def client() -> TestClient:
    """A FastAPI test client backed by a freshly constructed app."""
    return TestClient(create_app())


@pytest.fixture(scope="session")
def engine() -> Engine:
    """Session-scoped engine with extensions + schema created once.

    Skips the entire integration suite if Postgres is unreachable.
    """
    eng = create_engine(TEST_DATABASE_URL)
    try:
        connection = eng.connect()
    except OperationalError:
        pytest.skip("Postgres not available for integration tests")
    connection.close()

    with eng.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)

    yield eng
    eng.dispose()


@pytest.fixture
def db_session(engine: Engine) -> Session:
    """A function-scoped session wrapped in a transaction that is rolled back.

    Each test runs in isolation: writes are visible within the test but undone
    afterwards, so tests neither see nor leave shared state.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def api_client(engine: Engine) -> Iterator[tuple[TestClient, sessionmaker]]:
    """A TestClient wired to the test database, plus a sessionmaker for seeding.

    Starts each test from a clean slate (tables truncated) and overrides the
    app's ``get_db`` so endpoints commit to the test engine. Because endpoints
    commit for real, isolation is provided by truncating up-front rather than by
    a rolled-back transaction.
    """
    def _truncate() -> None:
        with engine.begin() as conn:
            conn.execute(
                text("TRUNCATE salons, services, salon_services RESTART IDENTITY CASCADE")
            )

    _truncate()  # clean slate before the test
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db() -> Iterator[Session]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app), session_factory
    finally:
        app.dependency_overrides.clear()
        _truncate()  # leave the DB clean for transactional tests
