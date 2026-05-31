"""FastAPI dependency providers.

Small factory functions wired into endpoints with ``Depends`` so handlers
declare what they need (a service) rather than how to build it.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.service_repository import ServiceRepository
from app.services.salon_service import SalonService
from app.services.search_service import SearchService


def get_salon_service(db: Session = Depends(get_db)) -> SalonService:
    """Provide a request-scoped :class:`SalonService`."""
    return SalonService(db)


def get_search_service(db: Session = Depends(get_db)) -> SearchService:
    """Provide a request-scoped :class:`SearchService` wired to configured AI."""
    return SearchService.from_settings(db)


def get_service_repository(db: Session = Depends(get_db)) -> ServiceRepository:
    """Provide a request-scoped :class:`ServiceRepository`."""
    return ServiceRepository(db)
