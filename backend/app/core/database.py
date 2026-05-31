"""Database engine and session management.

Exposes a configured SQLAlchemy engine, a session factory, and a FastAPI
dependency (:func:`get_db`) that yields a request-scoped session and always
closes it. Centralising this here keeps the rest of the app free of
connection-handling boilerplate.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# A single engine per process; pre-ping avoids handing out stale connections.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base class shared by all ORM models."""


def get_db() -> Iterator[Session]:
    """Yield a request-scoped database session (FastAPI dependency).

    The session is committed by the caller as needed and always closed when
    the request finishes, even on error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
