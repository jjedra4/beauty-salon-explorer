"""Data access for the Service taxonomy."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service import Service


class ServiceRepository:
    """Repository encapsulating all `Service` queries."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_all(self) -> list[Service]:
        """Return every service, ordered by category then name."""
        stmt = select(Service).order_by(Service.category, Service.name)
        return list(self._db.scalars(stmt))

    def get_by_slugs(self, slugs: list[str]) -> list[Service]:
        """Return the services matching the given slugs (order not guaranteed)."""
        if not slugs:
            return []
        stmt = select(Service).where(Service.slug.in_(slugs))
        return list(self._db.scalars(stmt))

    def get_or_create(self, slug: str, name: str, category: str) -> Service:
        """Fetch a service by slug, creating it if it does not exist.

        Used by the data pipeline when materializing the taxonomy. The caller
        is responsible for committing the session.
        """
        existing = self._db.scalar(select(Service).where(Service.slug == slug))
        if existing is not None:
            return existing
        service = Service(slug=slug, name=name, category=category)
        self._db.add(service)
        self._db.flush()
        return service
