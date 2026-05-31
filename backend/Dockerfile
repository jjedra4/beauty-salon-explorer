# syntax=docker/dockerfile:1
#
# Backend image: FastAPI served by uvicorn. Dependencies are installed with
# `uv` for speed and reproducibility. A non-root user runs the app.

FROM python:3.12-slim AS base

# uv: fast, reproducible Python package management (copied from official image).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first (cached layer) using only the project metadata.
COPY pyproject.toml ./
RUN uv pip install --system --no-cache -e .

# Copy the application source.
COPY . .

# Run as an unprivileged user.
RUN chmod +x entrypoint.sh \
    && useradd --create-home --uid 1000 appuser \
    && chown -R appuser /app
USER appuser

EXPOSE 8000

# Migrate + seed, then launch the API (see entrypoint.sh).
CMD ["./entrypoint.sh"]
