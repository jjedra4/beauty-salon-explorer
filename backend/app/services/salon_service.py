"""Salon business logic.

Sits between the API routers and the repositories: it validates input against
the domain (districts, service slugs), coordinates the repositories, and owns
the transaction boundary. Routers stay thin; repositories stay query-only.
"""

from sqlalchemy.orm import Session

from app.core.constants import WARSAW_DISTRICTS
from app.core.errors import BadRequestError, NotFoundError
from app.core.taxonomy import SERVICE_BY_SLUG, VALID_SERVICE_SLUGS
from app.models.salon import Salon
from app.models.service import Service
from app.repositories.salon_repository import SalonRepository
from app.repositories.service_repository import ServiceRepository
from app.schemas.salon import SalonUpdate


class SalonService:
    """Use-cases for listing, retrieving, and editing salons."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._salons = SalonRepository(db)
        self._services = ServiceRepository(db)

    def list_salons(
        self,
        *,
        district: str | None,
        service_slug: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Salon], int]:
        """Return a filtered, paginated page of salons and the total count."""
        return self._salons.list_salons(
            district=district, service_slug=service_slug, limit=limit, offset=offset
        )

    def get_salon(self, salon_id: int) -> Salon:
        """Return a salon by id or raise :class:`NotFoundError`."""
        salon = self._salons.get(salon_id)
        if salon is None:
            raise NotFoundError(f"Salon {salon_id} not found")
        return salon

    def update_salon(self, salon_id: int, payload: SalonUpdate) -> Salon:
        """Apply a partial update to a salon, validating domain constraints."""
        salon = self.get_salon(salon_id)

        values = payload.model_dump(exclude_unset=True, exclude={"service_slugs"})
        self._validate_district(values.get("district"))

        services = None
        if payload.service_slugs is not None:
            services = self._resolve_services(payload.service_slugs)

        self._salons.apply_update(salon, values, services)
        self._db.commit()
        self._db.refresh(salon)
        return salon

    def list_districts(self) -> list[str]:
        """Return the districts present in the data."""
        return self._salons.list_districts()

    # ── Validation helpers ───────────────────────────────────────────────────
    @staticmethod
    def _validate_district(district: str | None) -> None:
        if district is not None and district not in WARSAW_DISTRICTS:
            raise BadRequestError(f"Unknown district: {district!r}")

    def _resolve_services(self, slugs: list[str]) -> list[Service]:
        """Resolve slugs to service entities, rejecting any not in the taxonomy.

        Valid services are created on demand, so any taxonomy slug is assignable
        even if no seeded salon used it yet.
        """
        unique = list(dict.fromkeys(slugs))
        unknown = [slug for slug in unique if slug not in VALID_SERVICE_SLUGS]
        if unknown:
            raise BadRequestError(f"Unknown service slugs: {', '.join(unknown)}")
        return [
            self._services.get_or_create(
                SERVICE_BY_SLUG[slug].slug,
                SERVICE_BY_SLUG[slug].name,
                SERVICE_BY_SLUG[slug].category.value,
            )
            for slug in unique
        ]
