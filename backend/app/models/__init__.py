"""ORM models package.

Importing the models here ensures they are all registered on
``Base.metadata`` (so Alembic autogenerate and ``create_all`` see them) with a
single ``import app.models``.
"""

from app.models.salon import Salon
from app.models.service import Service, salon_services

__all__ = ["Salon", "Service", "salon_services"]
