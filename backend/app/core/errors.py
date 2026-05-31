"""Application error types and FastAPI handlers.

Services raise these framework-agnostic errors; the handlers registered here
translate them into consistent JSON responses. This keeps business logic free
of HTTP concerns while giving the API a uniform error shape.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for expected, mappable application errors."""

    status_code = 500

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class NotFoundError(AppError):
    """A requested resource does not exist."""

    status_code = 404


class BadRequestError(AppError):
    """The request was understood but is invalid (e.g. unknown service slug)."""

    status_code = 400


def register_exception_handlers(app: FastAPI) -> None:
    """Register handlers mapping :class:`AppError` subclasses to JSON responses."""

    @app.exception_handler(AppError)
    async def _handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
