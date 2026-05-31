"""Pydantic schemas for services."""

from pydantic import BaseModel, ConfigDict


class ServiceRead(BaseModel):
    """A service as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    category: str
