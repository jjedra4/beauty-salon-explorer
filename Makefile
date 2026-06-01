# Warsaw Beauty Salon Explorer — developer task runner.
# Run `make help` for the list of available targets.

.DEFAULT_GOAL := help
.PHONY: help up down logs build test test-backend test-frontend lint \
        backend-dev frontend-dev migrate pipeline seed e2e screenshots ai-check places-check

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

# ── Docker stack ───────────────────────────────────────────────────────────
up: ## Build and start the full stack (db + backend + frontend)
	docker compose up --build

down: ## Stop the stack and remove volumes
	docker compose down -v

logs: ## Tail logs from all services
	docker compose logs -f

build: ## Build all images without starting
	docker compose build

# ── Local development (without Docker) ─────────────────────────────────────
backend-dev: ## Run the backend with autoreload (requires local Postgres)
	cd backend && uv run uvicorn app.main:app --reload

frontend-dev: ## Run the Next.js dev server
	cd frontend && npm run dev

# ── Quality gates ──────────────────────────────────────────────────────────
test: test-backend test-frontend ## Run all test suites

test-backend: ## Run backend tests with coverage (gates at 80%)
	cd backend && uv run pytest --cov=app --cov=pipeline --cov-fail-under=80

test-frontend: ## Run frontend unit tests
	cd frontend && npm test

ai-check: ## Smoke-test the real OpenAI models (needs OPENAI_API_KEY in .env)
	cd backend && uv run pytest -m live tests/live/test_openai_live.py -v

places-check: ## Smoke-test the real Google Places API (needs GOOGLE_MAPS_API_KEY in .env)
	cd backend && uv run pytest -m live tests/live/test_google_places_live.py -v

e2e: ## Run Playwright end-to-end tests (brings the stack up first)
	docker compose up -d --build
	cd frontend && npx playwright install --with-deps chromium && npx playwright test

screenshots: ## Capture demo screenshots (stack must be running)
	cd frontend && node scripts/capture-screenshots.mjs

lint: ## Lint and type-check both apps
	cd backend && uv run ruff check . && uv run mypy app pipeline
	cd frontend && npm run lint

# ── Data pipeline (filled in across M1–M3) ─────────────────────────────────
migrate: ## Apply database migrations
	cd backend && uv run alembic upgrade head

pipeline: ## Run the data collection + AI enrichment pipeline
	cd backend && uv run python -m pipeline.run_pipeline

seed: ## Load the committed enriched seed dataset into the database
	cd backend && uv run python -m pipeline.seed
