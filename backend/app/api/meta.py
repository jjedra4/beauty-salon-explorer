"""Metadata endpoints that populate the frontend's filter controls."""

from fastapi import APIRouter, Depends

from app.api.deps import get_salon_service, get_service_repository
from app.repositories.service_repository import ServiceRepository
from app.schemas.service import ServiceRead
from app.services.salon_service import SalonService

router = APIRouter(tags=["meta"])


@router.get("/districts", response_model=list[str], summary="List districts in the data")
def list_districts(service_layer: SalonService = Depends(get_salon_service)) -> list[str]:
    """Return the distinct districts present in the dataset."""
    return service_layer.list_districts()


@router.get("/services", response_model=list[ServiceRead], summary="List service taxonomy")
def list_services(
    repository: ServiceRepository = Depends(get_service_repository),
) -> list[ServiceRead]:
    """Return the full service taxonomy for filtering."""
    return [ServiceRead.model_validate(service) for service in repository.list_all()]
