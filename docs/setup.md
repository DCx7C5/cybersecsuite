# CyberSecSuite Setup Guide

Complete walkthrough of every setup step — from a bare clone to a running server.

---

## Quick Start (for impatient developers)

```bash
# 1. Clone, configure environment, install deps, start DB
git clone https://github.com/DCx7C5/cybersecsuite.git && cd cybersecsuite
make env          # copy .env.example → .env (edit secrets before proceeding)
make setup        # install deps + start DB + schema + seed (runs steps 0–4)

# 2. Start the server (auto-runs first-time scaffold on first invocation)
make serve
```

> **`make setup`** is a convenience alias for `make env install db schema seed` in sequence.
> On first `make serve`, the `.css-initialized` sentinel is checked; if missing, `css-first-setup`
> runs automatically (see [What `make css-first-setup` Does](#what-make-css-first-setup-does)).

---

## Prerequisites

| Tool | Minimum version | Install |
|------|----------------|---------|
| **Python** | 3.14+ | <https://python.org> |
| **uv** | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Docker** | 24+ (with Compose v2) | <https://docs.docker.com/get-docker/> |
| **Node / npm** | 18+ (optional — dashboard TypeScript only) | <https://nodejs.org> |
| **git** | any | system package manager |

Verify with:

```bash
python --version   # Python 3.14.x
uv --version
docker compose version   # Docker Compose v2.x
```

---

## Environment Variables

Copy `.env.example` to `.env` (`make env`) and fill in the values marked **required**.

### PostgreSQL

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `CYBERSEC_DB_HOST` | `127.0.0.1` | Yes | DB host (use `/tmp` for Unix socket inside Docker) |
| `CYBERSEC_DB_PORT` | `5432` | Yes | PostgreSQL port |
| `CYBERSEC_DB_USER` | `cybersec` | Yes | DB user name |
| `CYBERSEC_DB_PASSWORD` | `change_me` | **Yes — change this** | DB password |
| `CYBERSEC_DB_NAME` | `cybersec_forensics` | Yes | Database name |

### Startup behaviour

| Variable | Default | Description |
|----------|---------|-------------|
| `CYBERSEC_AUTO_CREATE_DB` | `true` | Create DB + schema on first ASGI startup if missing (idempotent) |
| `CYBERSEC_BOOTSTRAP_INTEL_ON_START` | `false` | Re-seed MITRE/CVE intel on every ASGI start — set `false` after initial seed |

### Data directories

| Variable | Default | Description |
|----------|---------|-------------|
| `CYBERSEC_BASE_DIR` | `./data` | Root for runtime data files |
| `CYBERSEC_INTEL_DIR` | `./data/cybersec-shared/intelligence` | Directory scanned for MISP/STIX feed JSON files |
| `CYBERSEC_PROJECT_DIR` | `.` | Project working directory |

### Scope defaults

| Variable | Default | Description |
|----------|---------|-------------|
| `CYBERSEC_WORKSPACE` | `default` | Active workspace name |
| `CYBERSEC_PROJECT` | `default` | Active project name |
| `CYBERSEC_SESSION_ID` | _(unset)_ | Per-investigation session ID (set manually) |

### A2A server

| Variable | Default | Description |
|----------|---------|-------------|
| `CYBERSEC_A2A_BASE_URL` | `http://127.0.0.1:8000` | Public base URL for A2A agent card |
| `CYBERSEC_A2A_PORT` | `8000` | A2A server port |
| `ASGI_HOST` | `127.0.0.1` | uvicorn bind address |
| `ASGI_PORT` | `8000` | uvicorn HTTP port |
| `ASGI_TLS_PORT` | `8433` | uvicorn HTTPS port (only used when cert/key exist) |

### Observability

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENOBSERVE_OTLP_ENDPOINT` | `http://127.0.0.1:5080/api/default` | OTLP ingest endpoint for LLM traces |
| `OPENOBSERVE_EMAIL` | `admin@cybersec.local` | OpenObserve admin login |
| `OPENOBSERVE_PASSWORD` | `cYb3rS3c!` | OpenObserve admin password |
| `OTEL_SERVICE_NAME` | `cybersecsuite-llm` | OTEL service name in traces |

### AI provider keys (all optional, provide at least one for AI features)

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Claude (Anthropic) |
| `OPENAI_API_KEY` | GPT-* (OpenAI) |
| `GEMINI_API_KEY` | Gemini (Google) |
| `DEEPSEEK_API_KEY` | DeepSeek |
| `GROQ_API_KEY` | Groq (fast inference) |
| `MISTRAL_API_KEY` | Mistral AI |
| `XAI_API_KEY` | Grok (xAI) |
| `TOGETHER_API_KEY` | Together AI |
| `OPENROUTER_API_KEY` | OpenRouter |
| `NVIDIA_API_KEY` | NVIDIA NIM |
| `DYSTOPIAN_VAULT_PASSWORD` | Master password for the encrypted secret vault |

### Debug / QoL

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable verbose logging |
| `QOL_DEFAULT_TOGGLES` | _(unset)_ | Comma-separated default output toggles (e.g. `no_thinking,no_chat`) |
| `QOL_DEFAULT_SCOPE` | _(unset)_ | Default scope for QoL settings (`session`, `project`, `global`) |
| `QOL_MAX_TOKENS` | _(unset)_ | Max token budget for QoL directive block |

---

## Full Setup Walkthrough

### Step 0: Clone & configure environment

```bash
make env
```

**What it does:**
- Checks if `.env` already exists; skips silently if so.
- Copies `.env.example` → `.env` and sets file permissions to `600` (owner-read-only).
- Prints `"Created .env — fill in secrets before starting"`.

**What to edit before proceeding:**
- Change `CYBERSEC_DB_PASSWORD` from the placeholder `change_me`.
- Add at least one AI provider key (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.).
- Adjust `CYBERSEC_DB_HOST` / `CYBERSEC_DB_PORT` if you're not using the default Docker setup.

---

### Step 1: Install dependencies

```bash
make install
```

**What it does:**

Runs `uv sync --all-groups`, which:

1. Reads `pyproject.toml` and `uv.lock`.
2. Creates/updates `.venv/` in the project root with all packages, including dev and test groups.
3. Installs the project itself as an editable package, which registers CLI entry points:
   - `cybersecsuite` → `manage:main_sync`
   - `cybersec-mcp` → `csmcp.cybersec.server:main`
   - `cybersec-mcp-crypto` → `csmcp.dystopian_server:main`
   - `cybersec-proxy` → `ai_proxy.cli:main`

Key runtime dependencies include: `fastapi`, `starlette`, `uvicorn`, `tortoise-orm`, `asyncpg`,
`httpx`, `pydantic`, `cryptography`, `argon2-cffi`, `uvloop`, `anthropic`, `opentelemetry-sdk`.

For production-only (no dev/test tools):

```bash
make install-prod   # uv sync (no --all-groups)
```

For TypeScript dashboard development:

```bash
make install-ts     # npm install --save-dev typescript
```

---

### Step 2: Start the database

```bash
make db
```

**What it does:**

1. Runs `docker compose up -d cybersec-postgres` — starts **only** the PostgreSQL container
   (`cybersec-postgres`), not the full stack.
2. Waits for the container to pass its health check (or falls back to `sleep 5`).

**Container details:**

| Property | Value |
|----------|-------|
| Container name | `cybersec-postgres` |
| Image | Custom build from `.docker/postgres/Dockerfile` |
| Host port | `127.0.0.1:5432` (configurable via `POSTGRES_PORT` env var) |
| Data volume | `pg_data` (named Docker volume, persists across restarts) |
| Socket volume | `pg_socket` (shared with the proxy container when using Docker Compose full stack) |
| Health check | `pg_isready -U $POSTGRES_USER -d $POSTGRES_DB` every 30 s |

The database, user, and initial schema are created automatically using the values from `.env`
(`CYBERSEC_DB_USER`, `CYBERSEC_DB_PASSWORD`, `CYBERSEC_DB_NAME`).

To stop the DB:

```bash
make db-stop
```

---

### Step 3: Initialize schema

```bash
make schema
```

**What it does:**

Runs `uv run --no-project python src/manage.py schema`, which:

1. Connects to the PostgreSQL database using `CYBERSEC_DB_*` env vars.
2. Calls `asyncpg.connect` to the `postgres` system DB and creates `cybersec_forensics` if absent
   (`CYBERSEC_AUTO_CREATE_DB` path via `init_tortoise_async(create_db=True)`).
3. Runs Tortoise ORM's `generate_schemas(safe=True)` — creates all tables if they don't exist,
   does **not** drop or alter existing tables (fully idempotent).
4. Prints the count of registered tables.

**Example output:**

```
→ Creating/updating schemas...
✅ Done — 47 tables in public schema
```

**What tables are created:** All Tortoise ORM model classes registered under `db.models.*`,
including: cases, sessions, findings, IOCs, MITRE techniques/actors/software, CWE, CAPEC, CVE,
NIST CSF/AI RMF controls, PoC entries, audit logs, LLM call logs, API usage logs, tool registry,
marketplace, machines, and more.

Safe to re-run at any time — new models added during development will have their tables created
without affecting existing data.

---

### Step 4: Seed intelligence data

#### Basic seed (offline, fast)

```bash
make seed
```

Runs `python src/manage.py seed`, which calls `initialize_default_seed_data()` to load all
intelligence fixtures from **local JSON files** bundled in `src/db/fixtures/`. No network
required. All operations are idempotent (uses `get_or_create`).

| Dataset | Fixture file | Approximate size |
|---------|-------------|-----------------|
| NIST CSF 2.0 controls | `nist_csf_2.json` | 185 subcategories |
| NIST AI RMF 1.0 controls | `nist_ai_rmf.json` | 72 subcategories |
| MITRE ATT&CK techniques | `mitre_techniques.json` | 30 canonical entries |
| MITRE ATT&CK threat actors | `mitre_actors.json` | 12 entries |
| MITRE ATT&CK software | `mitre_software.json` | 14 entries |
| CWE weaknesses | `cwe_entries.json` | curated subset |
| CAPEC attack patterns | `capec_entries.json` | curated subset |
| CVE entries | `cve_entries.json` | curated subset |
| PoC exploit records | `poc_entries.json` | 5 entries |

**Example output:**

```
  ✅ nist_csf: 185 created, 0 skipped
  ✅ nist_ai_rmf: 72 created, 0 skipped
  ✅ mitre_techniques: 30 created, 0 skipped
  ...
✅ All intel tables seeded.
```

#### Intel-only seed (MITRE/CWE/CAPEC fixtures)

```bash
make seed-intel
```

A subset of the above: seeds only MITRE techniques, actors, software, CWE, and CAPEC from the
same local fixture files. Use this to refresh just the threat intel tables without touching NIST
or CVE data.

#### Full live-data seeds (network required, optional)

These fetch complete datasets from the internet and may take significant time:

```bash
make seed-intel        # fixture-based (offline, fast — as above)
uv run python src/manage.py seed-cwe           # full CWE DB from MITRE
uv run python src/manage.py seed-capec         # full CAPEC DB from MITRE
uv run python src/manage.py seed-mitre         # full MITRE ATT&CK (live)
uv run python src/manage.py seed-nvd-cves      # NVD API v2 (30+ min without API key)
uv run python src/manage.py seed-nvd-cves --api-key YOUR_KEY   # faster with key
```

> Get a free NVD API key at <https://nvd.nist.gov/developers/request-an-api-key> to increase
> rate limits from 5 req/30 s to 50 req/30 s.

---

### Step 5: Template scaffolding (automatic)

```bash
uv run python -m cybersecsuite.scaffold
```

**What it does:**

Copies embedded Markdown and JSON templates from `src/cybersecsuite/data/templates/` into
`.claude/templates/` in the current working directory (project root). This is non-destructive —
existing files are never overwritten.

**Templates installed:**

```
.claude/templates/
├── artifact.md                          # artifact capture template
├── baselines/
│   ├── kernel.md                        # kernel baseline
│   ├── network.md                       # network baseline
│   ├── persistence.md                   # persistence baseline
│   └── processes.md                     # process baseline
├── iocs/
│   ├── cleared.md                       # cleared IOC list
│   ├── ioc-db.md                        # IOC database template
│   └── watchlist.md                     # active watchlist
├── project/
│   └── findings.md                      # investigation findings
├── reports/
│   └── investigation-report.md          # final investigation report
├── session/
│   ├── session-manifest.json            # session metadata
│   └── timeline.md                      # event timeline
└── threat-intelligence/
    ├── session-index.md                 # per-session TI index
    └── threat-profile.md               # threat actor/campaign profile
```

These templates are used by the MCP template server and Claude agent workflows.

---

## First-Run Detection

### `.css-initialized` sentinel

The Makefile targets `serve`, `test`, and `docker-up` all declare `.css-initialized` as a
prerequisite:

```make
serve: .css-initialized
```

Make treats `.css-initialized` as a file target. If the file does not exist in the project root,
Make automatically runs the `css-first-setup` target to create it. This means **the first time
you run `make serve`, full first-time setup is triggered automatically**.

### Python-level first-run (`startup/first_run.py`)

Independently, the ASGI application itself checks for `~/.cybersecsuite/` on every startup:

```python
is_first = not base_dir.exists()   # ~/.cybersecsuite/
```

If the directory is absent, `first_run_setup()` creates it with subdirectories
(`sessions`, `templates`, `cache`, `logs`) and writes a blank `marketplace.json`.

On subsequent starts, `first_run_setup()` loads `~/.cybersecsuite/marketplace.json` into memory
and calls `accounts.sync.sync_providers_to_db()` to sync configured AI providers to the DB.

---

## What `make css-first-setup` Does

This is the one-time application bootstrap. It runs automatically on the first `make serve`
(or can be run manually). It executes five steps in order:

### [1/5] Install app home

```bash
uv run --no-project python src/manage.py install
```

Creates the `~/.cybersecsuite/` directory tree with `chmod 700` on every directory:

```
~/.cybersecsuite/
├── sessions/               # per-investigation session state
├── memory/
│   ├── system/             # system-level agent memory
│   ├── project/            # project-scoped memory
│   └── session/            # session-scoped memory
├── vault/
│   ├── memories/           # encrypted memory blobs
│   └── wiki/               # vault wiki pages
├── cache/                  # transient cache files
├── logs/                   # application logs
├── data/
│   ├── projects/           # project data
│   └── workspaces/         # workspace data
├── skills/                 # app-scoped skills index
├── providers/              # provider configuration
└── .cybersecsuite          # JSON marker: version + installed_at timestamp
```

Override the location with `CYBERSECSUITE_HOME=/path/to/dir`. Safe to re-run.

### [2/5] Patch Claude settings

```bash
python3 -c "... sets CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 in ~/.claude/settings.json ..."
```

Reads `~/.claude/settings.json` (creates it if absent), then sets
`env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"` under the `env` key. This enables Claude
Code's multi-agent team feature required for A2A agent orchestration. Existing settings are
preserved.

### [3/5] DB schema

```bash
uv run --no-project python src/manage.py schema
```

Same as `make schema` (see [Step 3](#step-3-initialize-schema)). Creates all Tortoise ORM tables.

### [4/5] DB seed

```bash
uv run --no-project python src/manage.py seed
```

Same as `make seed` (see [Step 4](#step-4-seed-intelligence-data)). Loads all fixture-based
intel data from local JSON files.

### [5/5] Scaffold project templates

```bash
uv run python -m cybersecsuite.scaffold
```

Copies embedded templates into `.claude/templates/` (see [Step 5](#step-5-template-scaffolding-automatic)).

After all five steps, `.css-initialized` is written (via `touch`) and the script prints:

```
✅ css-first-setup complete. Run 'make serve' to start.
```

---

## Post-Setup Verification

### Check the DB is up and seeded

```bash
make status
```

Example output:
```
Initialized : True
Intel Seeded: False
DB          : cybersec_forensics @ 127.0.0.1:5432
Tables (47): audit_logs, capec_attack_patterns, case_intakes, ...
Intel counts:
  - mitre_techniques: 30
  - mitre_actors: 12
  ...
```

### Check the ASGI server health

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"status": "ok", "initialized": true, "config": {"host": "127.0.0.1", "port": 5432, "database": "cybersec_forensics"}}
```

### Run the test suite

```bash
make test
```

Requires `.css-initialized` to exist (auto-creates it if not). Runs `pytest` against `tests/`.

### List configured AI providers

```bash
make proxy-providers
```

### Verify templates were scaffolded

```bash
ls .claude/templates/
# artifact.md  baselines/  iocs/  project/  reports/  session/  threat-intelligence/
```

### Verify app home

```bash
ls ~/.cybersecsuite/
# cache/  data/  logs/  memory/  providers/  sessions/  skills/  vault/  .cybersecsuite
```

---

## Directory Structure After Setup

### App home (`~/.cybersecsuite/`)

Created by `manage.py install` (step 1 of `css-first-setup`):

```
~/.cybersecsuite/
├── .cybersecsuite           # JSON marker: {"version": "1.0", "installed_at": "..."}
├── cache/                   # transient HTTP cache, computed data
├── data/
│   ├── projects/            # per-project runtime data
│   └── workspaces/          # per-workspace runtime data
├── logs/                    # application log files
├── marketplace.json         # loaded marketplace registry (providers/skills/agents)
├── memory/
│   ├── project/             # project-scoped agent memory
│   ├── session/             # session-scoped agent memory
│   └── system/              # system-level agent memory
├── providers/               # provider config files
├── sessions/                # investigation session state
├── skills/                  # app-scoped skills directory
├── skills-index.json        # merged skill index (built by `manage.py build-skill-index`)
└── vault/
    ├── memories/            # encrypted memory blobs (Ed25519 signed)
    └── wiki/                # vault wiki pages
```

### Project templates (`.claude/templates/`)

Created by `python -m cybersecsuite.scaffold` (step 5 of `css-first-setup`):

```
.claude/templates/
├── artifact.md
├── baselines/
│   ├── kernel.md
│   ├── network.md
│   ├── persistence.md
│   └── processes.md
├── iocs/
│   ├── cleared.md
│   ├── ioc-db.md
│   └── watchlist.md
├── project/
│   └── findings.md
├── reports/
│   └── investigation-report.md
├── session/
│   ├── session-manifest.json
│   └── timeline.md
└── threat-intelligence/
    ├── session-index.md
    └── threat-profile.md
```

---

## First Start (`make serve`)

What happens in order when you run `make serve` for the first time after setup:

```bash
make serve
```

1. **`.css-initialized` check** — Make checks for the sentinel file. If absent,
   `css-first-setup` runs automatically (all 5 steps above), then `touch .css-initialized`.

2. **uvicorn starts** — Runs:
   ```
   uv run uvicorn proxy.asgi:app --host 127.0.0.1 --port 8000 --reload --app-dir src
   ```

3. **ASGI `_on_startup()` fires:**
   - **First-run detection** — `first_run_setup()` in `startup/first_run.py` checks if
     `~/.cybersecsuite/` exists. Creates it and `marketplace.json` on first run, otherwise
     loads the existing marketplace.
   - **Provider sync** — `accounts.sync.sync_providers_to_db()` upserts configured AI
     providers from `.env` into the database.
   - **IPC server** — `hooks.ipc_receiver.ensure_ipc_server()` starts the inter-process
     communication socket (non-fatal if unavailable).
   - **DB init** — `init_tortoise_async()` connects Tortoise ORM to PostgreSQL. If
     `CYBERSEC_AUTO_CREATE_DB=true`, creates the database and runs `generate_schemas` too.
   - **Rate limiter config** — Each enabled AI provider's RPM/TPM limits are loaded into the
     in-memory `rate_limiter`.
   - **Telemetry** — `TelemetryCollector.start()` begins background telemetry collection.
   - **OTEL tracing** — `llm.otel.setup_otel()` configures OpenTelemetry (non-fatal).
   - **OpenObserve** — `openobserve.streams.ensure_streams()` creates log streams and starts
     the background flush loop (non-fatal if OpenObserve is not running).

4. **Routes available:**
   - `GET /health` — liveness + DB health check
   - `GET /.well-known/agent.json` — A2A agent card discovery
   - `POST /a2a/*` — A2A JSON-RPC agent endpoints
   - `GET /a2a/*/stream` — A2A SSE event stream
   - `POST /v1/chat/completions` — OpenAI-compatible AI proxy
   - `GET /v1/models` — list available models
   - All other `/v1/*` routes — OpenAI-compatible AI proxy

---

## MCP Core Setup (optional, separate script)

The 7 core MCPs are installed from the companion `ai-marketplace` repository:

```bash
# Clone the marketplace first
git clone https://github.com/DCx7C5/ai-marketplace.git ~/Projects/ai-marketplace

# Run the installer
bash scripts/deploy/install-mcp-core.sh [--verbose] [--offline] [--verify-only]
```

MCPs installed (requires `~/Projects/ai-marketplace/mcps/*` to exist):

| MCP | Source |
|-----|--------|
| `csscore-mcp` | `ai-marketplace/mcps/csscore-mcp` |
| `canvas-mcp` | `ai-marketplace/mcps/canvas-mcp` |
| `memory-mcp` | `ai-marketplace/mcps/memory-mcp` |
| `template-mcp` | `ai-marketplace/mcps/template-mcp` |
| `playwright-mcp` | `ai-marketplace/mcps/playwright-mcp` |
| `dystopian-crypto-mcp` | `ai-marketplace/mcps/dystopian-crypto-mcp` |
| `custom-mcp` | `src/csmcp/mcps/custom-mcp` (bundled) |

The script runs preflight checks (uv present, Python ≥ 3.11, both repo directories exist),
installs each MCP via `uv pip install -e .`, verifies `import <mcp_module>` succeeds, and
prints a summary report. Exits with code `0` on full success, `1` on partial/complete failure.

---

## Full Docker Stack (all services)

To run the entire stack (DB + app + dashboard + Redis + Ollama + OpenObserve):

```bash
make docker-build   # build images first
make docker-up      # docker compose up -d (all services)
```

Services started:

| Container | Port (host) | Description |
|-----------|-------------|-------------|
| `cybersec-postgres` | `127.0.0.1:5432` | PostgreSQL 16 |
| `cybersec-redis` | `127.0.0.1:6379` | Redis (session cache, queues) |
| `cybersec-proxy` | `127.0.0.1:8765` | ASGI app (AI proxy + A2A) |
| `cybersec-dashboard` | `127.0.0.1:8000`, `127.0.0.1:8443` | React frontend |
| `cybersec-ollama` | `127.0.0.1:11434` | Ollama (local LLM inference, GPU optional) |
| `cybersec-openobserve` | `127.0.0.1:5080` | OpenObserve (LLM telemetry, logs) |

> The `cybersec-proxy` container connects to PostgreSQL via Unix socket (`pg_socket` volume)
> rather than TCP when running in the full stack.

---

## Troubleshooting

### Docker not running

**Symptom:** `make db` fails with `Cannot connect to the Docker daemon`.

**Fix:** Start Docker.
```bash
sudo systemctl start docker   # Linux systemd
# or open Docker Desktop (macOS/Windows)
```

---

### Port 5432 already in use

**Symptom:** `make db` → container exits with `address already in use`.

**Fix:** Either stop the local Postgres or override the host port:
```bash
# Identify what's using 5432
sudo lsof -i :5432
# Override the host port (add to .env):
POSTGRES_PORT=5433
```

---

### DB connection refused

**Symptom:** `make schema` or `make seed` fails with `Connection refused` or
`could not connect to server`.

**Fix:**
1. Check the DB container is running: `docker compose ps cybersec-postgres`
2. Wait for the health check to pass: `docker compose logs -f cybersec-postgres`
3. Verify `.env` values match the container config (`CYBERSEC_DB_HOST`, `CYBERSEC_DB_PORT`,
   `CYBERSEC_DB_USER`, `CYBERSEC_DB_PASSWORD`).

---

### Permission denied on `~/.cybersecsuite`

**Symptom:** `manage.py install` fails with `PermissionError`.

**Fix:** The directory was probably created by a different user (e.g., Docker root). Remove and
re-run:
```bash
rm -rf ~/.cybersecsuite
make css-first-setup
```

---

### `uv` not found

**Symptom:** `make install` fails with `uv: command not found`.

**Fix:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# then reload your shell
source ~/.bashrc   # or ~/.zshrc
```

---

### `ANTHROPIC_API_KEY` not set (or other AI key missing)

**Symptom:** `make serve` starts but AI proxy returns `401 Unauthorized` or
`provider not configured`.

**Fix:** Add the key to `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```
Then restart: `make serve`. The proxy supports 10 providers — at least one key is needed for
AI features. Use `make proxy-providers` to see which are active.

---

### Template not found error

**Symptom:** MCP template server returns `template not found` for a known template name.

**Fix:** Re-run the scaffold step to copy any missing templates:
```bash
uv run python -m cybersecsuite.scaffold
```
The scaffold never overwrites existing files, so re-running is safe.

---

### "relation does not exist" DB error

**Symptom:** Any DB query fails with `asyncpg.exceptions.UndefinedTableError: relation "X" does not exist`.

**Fix:** Run schema creation (idempotent):
```bash
make schema
```
If the error persists after schema creation, check that the DB container is still running and
that `CYBERSEC_DB_NAME` in `.env` matches the database the container created.

---

### `.css-initialized` missing after running setup

**Symptom:** `make serve` keeps re-running `css-first-setup` on every invocation.

**Fix:** The sentinel file lives in the project root. Create it manually after a successful
manual setup:
```bash
touch .css-initialized
```
Or run `make css-first-setup` directly — it `touch`es the file on success.

---

### Python version mismatch

**Symptom:** `uv sync` fails with `Requires-Python >=3.14`.

**Fix:** Install Python 3.14+:
```bash
uv python install 3.14
uv python pin 3.14
uv sync --all-groups
```

---

## Reference: All `manage.py` Commands

```
python src/manage.py <command>

Setup:
  install           Create ~/.cybersecsuite/ directory structure (idempotent)
  schema            Create / update all DB tables (generate_schemas safe=True)
  init-db           One-shot: schema + all fixture seeds
  seed              Seed all intel fixtures (NIST + MITRE + CWE + CAPEC + CVE + PoC)
  seed-all          Same as seed + tool registry + API service models
  seed-intel        Seed MITRE techniques, actors, software, CWE, CAPEC (fixtures)
  seed-nist-csf     Seed NIST CSF 2.0 (185 subcategories)
  seed-nist-ai-rmf  Seed NIST AI RMF 1.0 (72 subcategories)
  seed-mitre        Seed MITRE ATT&CK from live data (network)
  seed-cwe          Seed full CWE database from MITRE (network)
  seed-capec        Seed full CAPEC database from MITRE (network)
  seed-nvd-cves     Seed CVEs from NVD API v2 (network, slow without API key)
  seed-poc          Seed PoC exploit sample records

Operations:
  status            Show DB status and table row counts
  machine           Seed and display local machine hardware inventory
  shell             Interactive Python shell with all models loaded
  case-open         Open a new investigation case (interactive intake)
  team-task         Dispatch task to blue/red/purple team

Security:
  ssl create-ca     Create CA keypair (Ed25519, password-protected)
  ssl create-key    Create Ed25519 keypair
  ssl list          List all managed keys
  vault store       Encrypt and store a secret
  vault get         Decrypt and print a secret
  vault list        List vault secrets
  check             Run model, fixture, and config integrity checks
```
