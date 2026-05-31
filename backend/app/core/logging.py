"""Logging configuration.

Provides a single :func:`configure_logging` entry point that installs a
consistent, timestamped log format across the application and the data
pipeline. Kept dependency-free (standard library only) for simplicity.
"""

import logging

from app.core.config import settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(level: str | None = None) -> None:
    """Configure the root logger once for the whole process.

    Args:
        level: Optional override for the log level. Defaults to the value in
            application settings (``LOG_LEVEL``).
    """
    logging.basicConfig(
        level=(level or settings.log_level).upper(),
        format=_LOG_FORMAT,
        datefmt=_DATE_FORMAT,
        force=True,  # replace any handlers installed by uvicorn/pytest
    )
    # uvicorn installs its own access logger; align it with our level.
    logging.getLogger("uvicorn.access").setLevel((level or settings.log_level).upper())


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger (thin wrapper for a single import site)."""
    return logging.getLogger(name)
