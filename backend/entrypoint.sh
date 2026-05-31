#!/bin/sh
# Container entrypoint: prepare the database, then start the API.
# Runs migrations and seeds the committed dataset (idempotent — seeding is
# skipped if the database already has salons) so `docker compose up` yields a
# working app with data and no manual steps.
set -e

echo "[entrypoint] Applying database migrations…"
alembic upgrade head

echo "[entrypoint] Seeding database (skipped if already populated)…"
python -m pipeline.seed

echo "[entrypoint] Starting API…"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
