"""Data access for salons.

The repository is the only layer that talks to SQLAlchemy for salons. It
exposes typed methods for the queries the application needs (get, filtered
list, update, distinct districts) and hides query construction from services.
Vector/keyword search methods are added in M5.
"""

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.salon import Salon
from app.models.service import Service
from app.schemas.search import SearchFilters


class SalonRepository:
    """Repository encapsulating all `Salon` queries."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── Reads ──────────────────────────────────────────────────────────────
    def get(self, salon_id: int) -> Salon | None:
        """Return a salon by primary key, or ``None`` if absent."""
        return self._db.get(Salon, salon_id)

    def get_by_source(self, source: str, source_id: str) -> Salon | None:
        """Return a salon by its (source, source_id) provenance key."""
        stmt = select(Salon).where(Salon.source == source, Salon.source_id == source_id)
        return self._db.scalar(stmt)

    def list_salons(
        self,
        *,
        district: str | None = None,
        service_slug: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Salon], int]:
        """Return a page of salons matching the filters, plus the total count.

        Args:
            district: Optional exact-match district filter.
            service_slug: Optional filter for salons offering this service.
            limit: Page size.
            offset: Number of rows to skip.

        Returns:
            A ``(salons, total)`` tuple where ``total`` is the unpaginated count.
        """
        stmt = self._apply_filters(select(Salon), district, service_slug)

        total = self._db.scalar(
            self._apply_filters(select(func.count(Salon.id)), district, service_slug)
        )

        page_stmt = stmt.order_by(Salon.name).limit(limit).offset(offset)
        salons = list(self._db.scalars(page_stmt).unique())
        return salons, int(total or 0)

    def list_districts(self) -> list[str]:
        """Return the distinct districts present in the data, sorted."""
        stmt = select(Salon.district).distinct().order_by(Salon.district)
        return list(self._db.scalars(stmt))

    # ── Search ─────────────────────────────────────────────────────────────
    def vector_search(
        self, embedding: list[float], filters: SearchFilters, limit: int
    ) -> list[tuple[Salon, float]]:
        """Rank salons by embedding cosine distance, applying hard filters.

        Only salons that have an embedding are considered. Returns
        ``(salon, distance)`` pairs ordered nearest-first.
        """
        distance = Salon.embedding.cosine_distance(embedding).label("distance")
        stmt = select(Salon, distance).where(Salon.embedding.is_not(None))
        stmt = self._apply_search_filters(stmt, filters)
        stmt = stmt.order_by(distance).limit(limit)
        return [(row[0], float(row[1])) for row in self._db.execute(stmt).unique().all()]

    def keyword_search(
        self, query: str, filters: SearchFilters, limit: int
    ) -> list[tuple[Salon, float]]:
        """Fallback search: trigram/substring match on name + service text.

        Ranks by trigram name similarity. Returns ``(salon, similarity)`` pairs.
        """
        pattern = f"%{query}%"
        similarity = func.similarity(Salon.name, query).label("similarity")
        stmt = select(Salon, similarity).where(
            or_(
                Salon.name.ilike(pattern),
                Salon.raw_services_text.ilike(pattern),
                Salon.district.ilike(pattern),
                func.similarity(Salon.name, query) > 0.1,
            )
        )
        stmt = self._apply_search_filters(stmt, filters)
        stmt = stmt.order_by(similarity.desc()).limit(limit)
        return [(row[0], float(row[1])) for row in self._db.execute(stmt).unique().all()]

    # ── Writes ─────────────────────────────────────────────────────────────
    def add(self, salon: Salon) -> Salon:
        """Persist a new salon (flush only; caller commits)."""
        self._db.add(salon)
        self._db.flush()
        return salon

    def apply_update(
        self,
        salon: Salon,
        values: dict[str, object],
        services: list[Service] | None,
    ) -> Salon:
        """Apply a partial update to a salon in place.

        Args:
            salon: The managed salon instance to mutate.
            values: Scalar field updates (already validated).
            services: If not ``None``, replaces the salon's service list.

        The caller commits the surrounding transaction.
        """
        for field, value in values.items():
            setattr(salon, field, value)
        if services is not None:
            salon.services = services
        self._db.flush()
        return salon

    # ── Internals ──────────────────────────────────────────────────────────
    @staticmethod
    def _apply_filters(
        stmt: Select,
        district: str | None,
        service_slug: str | None,
    ) -> Select:
        """Apply the shared district/service filters to a select statement."""
        if district:
            stmt = stmt.where(Salon.district == district)
        if service_slug:
            stmt = stmt.where(Salon.services.any(Service.slug == service_slug))
        return stmt

    @staticmethod
    def _apply_search_filters(stmt: Select, filters: SearchFilters) -> Select:
        """Apply structured search filters (district/services/price/rating)."""
        if filters.district:
            stmt = stmt.where(Salon.district == filters.district)
        if filters.service_slugs:
            stmt = stmt.where(Salon.services.any(Service.slug.in_(filters.service_slugs)))
        if filters.price_range:
            stmt = stmt.where(Salon.price_range == filters.price_range)
        if filters.min_rating is not None:
            stmt = stmt.where(Salon.rating >= filters.min_rating)
        return stmt
