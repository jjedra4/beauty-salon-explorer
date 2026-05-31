"""Salon endpoints: list (filter + paginate), detail, and partial update."""

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_salon_service
from app.schemas.salon import PaginatedSalons, SalonDetail, SalonSummary, SalonUpdate
from app.services.salon_service import SalonService

router = APIRouter(prefix="/salons", tags=["salons"])


@router.get("", response_model=PaginatedSalons, summary="List salons")
def list_salons(
    district: str | None = Query(None, description="Filter by district (exact match)."),
    service: str | None = Query(None, description="Filter by service slug."),
    limit: int = Query(20, ge=1, le=100, description="Page size."),
    offset: int = Query(0, ge=0, description="Rows to skip."),
    service_layer: SalonService = Depends(get_salon_service),
) -> PaginatedSalons:
    """Return a filtered, paginated list of salon summaries."""
    salons, total = service_layer.list_salons(
        district=district, service_slug=service, limit=limit, offset=offset
    )
    return PaginatedSalons(
        items=[SalonSummary.model_validate(salon) for salon in salons],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{salon_id}", response_model=SalonDetail, summary="Get salon details")
def get_salon(
    salon_id: int,
    service_layer: SalonService = Depends(get_salon_service),
) -> SalonDetail:
    """Return full details for a single salon (404 if not found)."""
    return SalonDetail.model_validate(service_layer.get_salon(salon_id))


@router.patch("/{salon_id}", response_model=SalonDetail, summary="Update a salon")
def update_salon(
    salon_id: int,
    payload: SalonUpdate,
    service_layer: SalonService = Depends(get_salon_service),
) -> SalonDetail:
    """Apply a partial update and persist it (404 if not found, 400 if invalid)."""
    return SalonDetail.model_validate(service_layer.update_salon(salon_id, payload))
