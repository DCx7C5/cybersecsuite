# CyberSecSuite — development commands
# Usage: make <target>
# Requires: uv, docker (for `make db`)

SHELL       := /bin/bash
PROJECT_DIR := $(shell pwd)
SRC_DIR     := $(PROJECT_DIR)/src
HOOKS_DIR   := /home/daen/Projects/AI
PYTHON_PATH := $(SRC_DIR):$(HOOKS_DIR)
UV          := uv
UVICORN_HOST ?= 127.0.0.1
UVICORN_PORT ?= 8000

export PYTHONPATH := $(PYTHON_PATH)

# ── Setup ─────────────────────────────────────────────────────────────────────

.PHONY: install
install:  ## Install all runtime + dev dependencies
	$(UV) sync --all-groups

.PHONY: install-prod
install-prod:  ## Install runtime dependencies only
	$(UV) sync

.PHONY: env
env:  ## Create .env from .env.example (skip if exists)
	@test -f .env && echo ".env already exists — skipping" || (cp .env.example .env && chmod 600 .env && echo "Created .env — fill in secrets before starting")

# ── Database ──────────────────────────────────────────────────────────────────

.PHONY: db
db:  ## Start PostgreSQL via Docker Compose
	docker compose up -d cybersec-postgres
	@echo "Waiting for Postgres to be healthy..."
	@docker compose wait cybersec-postgres 2>/dev/null || sleep 5

.PHONY: db-stop
db-stop:  ## Stop PostgreSQL container
	docker compose stop cybersec-postgres

.PHONY: schema
schema:  ## Create / update DB schema (idempotent)
	$(UV) run --no-project python src/manage.py schema

.PHONY: seed
seed:  ## Seed defaults + bootstrap intelligence data
	$(UV) run --no-project python src/manage.py seed

.PHONY: seed-intel
seed-intel:  ## Bootstrap MITRE/CVE/CWE intelligence only
	$(UV) run --no-project python src/manage.py seed-intel

.PHONY: status
status:  ## Show database status and table counts
	$(UV) run --no-project python src/manage.py status

.PHONY: machine
machine:  ## Seed local machine hardware inventory
	$(UV) run --no-project python src/manage.py machine

# ── Run ───────────────────────────────────────────────────────────────────────

.PHONY: serve
serve: .css-initialized  ## Start the ASGI server (A2A + AI proxy at /v1/)
	$(UV) run uvicorn proxy.asgi:app \
		--host $(UVICORN_HOST) \
		--port $(UVICORN_PORT) \
		--reload \
		--app-dir src

.PHONY: mcp
mcp:  ## Start the MCP server (stdio transport for Claude)
	$(UV) run python mcp_server.py

.PHONY: proxy-providers
proxy-providers:  ## List configured AI providers
	$(UV) run python -m ai_proxy.cli providers

.PHONY: proxy-models
proxy-models:  ## List available AI models
	$(UV) run python -m ai_proxy.cli models

.PHONY: proxy-chat
proxy-chat:  ## Chat via CLI (usage: make proxy-chat PROMPT="hello")
	$(UV) run python -m ai_proxy.cli chat "$(PROMPT)" -v

.PHONY: docker-up
docker-up: .css-initialized  ## Start all services (DB + app) via Docker Compose
	docker compose up -d

.PHONY: docker-down
docker-down:  ## Stop all Docker Compose services
	docker compose down

.PHONY: docker-build
docker-build:  ## Build Docker images
	docker compose build

.PHONY: shell
shell:  ## Interactive Python shell with all models loaded
	$(UV) run --no-project python src/manage.py shell

# ── Testing ───────────────────────────────────────────────────────────────────

.PHONY: test
test: .css-initialized  ## Run all tests (excluding legacy)
	$(UV) run --group test pytest --ignore=tests/legacy

.PHONY: test-legacy
test-legacy:  ## Run legacy (broken/pre-existing failures) tests only
	$(UV) run --group test pytest tests/legacy/

.PHONY: test-unit
test-unit:  ## Run unit tests only
	$(UV) run --group test pytest tests/unit/

.PHONY: test-integration
test-integration:  ## Run integration tests only
	$(UV) run --group test pytest tests/integration/

.PHONY: test-cov
test-cov:  ## Run tests with HTML coverage report
	$(UV) run --group test pytest --ignore=tests/legacy --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report: htmlcov/index.html"

.PHONY: test-crypto
test-crypto:  ## Run crypto tests only
	$(UV) run --group test pytest tests/scope/test_crypto.py -v

# ── Dashboard ─────────────────────────────────────────────────────────────────

.PHONY: dashboard
dashboard:  ## Generate static dashboard HTML
	$(UV) run --no-project python src/manage.py dashboard

.PHONY: dashboard-serve
dashboard-serve:  ## Generate and serve dashboard on port 9000
	$(UV) run --no-project python src/manage.py dashboard --serve --port 9000

# ── TypeScript ────────────────────────────────────────────────────────────────

.PHONY: install-ts
install-ts:  ## Install TypeScript dev dependencies (npm)
	npm install --save-dev typescript

.PHONY: build-ts
build-ts:  ## Compile dashboard TypeScript → static/js/
	cd src/dashboard && npx tsc -p tsconfig.json

.PHONY: watch-ts
watch-ts:  ## Watch and recompile TypeScript on change
	cd src/dashboard && npx tsc -p tsconfig.json --watch

.PHONY: lint-ts
lint-ts:  ## Type-check TypeScript without emitting
	cd src/dashboard && npx tsc -p tsconfig.json --noEmit

# DEPRECATED: ts_api is unused — planned for deletion in Phase 13.
# See docs/TS_API_ANALYSIS.md for rationale.
.PHONY: ts-api-start
ts-api-start:  ## [DEPRECATED] Start TypeScript SDK API server (port 8765)
	cd src/ts_api && npm start

.PHONY: ts-api-dev
ts-api-dev:  ## [DEPRECATED] Start TypeScript SDK API server with hot reload
	cd src/ts_api && npm run dev

# ── Code quality ──────────────────────────────────────────────────────────────

.PHONY: lint
lint:  ## Lint with ruff
	$(UV) run --group dev ruff check src/ tests/

.PHONY: fmt
fmt:  ## Auto-format with ruff
	$(UV) run --group dev ruff format src/ tests/

# ── First-time setup ──────────────────────────────────────────────────────────

.css-initialized:
	@$(MAKE) --no-print-directory css-first-setup
	@touch .css-initialized

.PHONY: css-first-setup
css-first-setup:  ## One-time app + DB setup (auto-triggered on first make run)
	@echo "==> [1/5] Installing app home (CYBERSECSUITE_HOME=~/.cybersecsuite)..."
	$(UV) run --no-project python src/manage.py install
	@echo "==> [2/5] Patching ~/.claude/settings.json..."
	@python3 -c "\
import json, pathlib; \
p = pathlib.Path.home() / '.claude' / 'settings.json'; \
d = json.loads(p.read_text()) if p.exists() else {}; \
env = d.setdefault('env', {}); \
env.setdefault('CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS', '1'); \
p.parent.mkdir(parents=True, exist_ok=True); \
p.write_text(json.dumps(d, indent=2) + '\n'); \
print('  OK: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS set')"
	@echo "==> [3/5] DB schema..."
	$(UV) run --no-project python src/manage.py schema
	@echo "==> [4/5] DB seed..."
	$(UV) run --no-project python src/manage.py seed
	@echo "==> [5/7] Scaffolding project templates..."
	$(UV) run python -m cybersecsuite.scaffold
	@echo "==> [6/7] Installing core MCPs..."
	@bash scripts/deploy/install-mcp-core.sh
	@echo "==> [7/7] Seeding marketplace from search-index.json..."
	$(UV) run --no-project python src/manage.py seed-marketplace
	@touch .css-initialized
	@echo ""
	@echo "✅ css-first-setup complete. Run 'make serve' to start."

.PHONY: setup
setup: env install db schema seed  ## Full first-run setup: env + deps + db + schema + seed
	@echo ""
	@echo "✅ Setup complete!"
	@echo "   Run 'make serve'             to start the A2A + AI proxy server"
	@echo "   Run 'make mcp'               to start the MCP server"
	@echo "   Run 'make proxy-providers'    to list configured AI providers"
	@echo "   Run 'cybersec-proxy chat \"hello\"'  to chat via CLI"

# ── Help ──────────────────────────────────────────────────────────────────────

.PHONY: help
help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
