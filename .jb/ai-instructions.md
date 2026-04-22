# CyberSecSuite — AI Context (v1.4)

Full-stack cybersecurity forensics platform.

## Stack
- **Python 3.14**, `uv` only (never `pip` or `poetry`)
- **TypeScript**, never JavaScript in the codebase (except for browser plugin)
- **ASGI** — Starlette, port 8000 (`src/proxy/asgi.py`)
- **MCP server** — 83+ tools, single `mcp__cybersec__*` namespace (`src/csmcp/`)
- **AI proxy** — 60 providers, 13 routing strategies, circuit breaker (`src/ai_proxy/`)
- **A2A protocol** — JSON-RPC 2.0 agent communication (`src/a2a/`)
- **PostgreSQL** — Tortoise ORM, ~41 models (`src/db/models/`) — relational + operational data only
- **OpenObserve** — observability sink for all append-only/time-series data (`src/openobserve/`)
- **OpenSearch** — Wazuh only (`--profile wazuh`); not used by the app
- **Crypto** — Ed25519 + BLAKE2b-256 + Argon2id + AES-256-GCM (`src/crypto/`)
- **Dashboard** — REST + SSE live monitoring (`src/dashboard/`)

## Data Storage Rules
- **PostgreSQL**: relational data, FK-linked models, intel KB, findings, IOCs, cases
- **OpenObserve**: ALL append-only/time-series data — audit events, API usage, LLM calls, intel update logs
- Never add a new PG table for time-series or audit-trail data — use `openobserve/writer.py::bulk_index(stream_base, docs)` instead
- Register new streams in `src/openobserve/streams.py` STREAMS list

## OpenObserve Streams
| Stream base         | Data                              | Writer                         |
|---------------------|-----------------------------------|--------------------------------|
| `telemetry`         | In-process OTEL metrics           | `openobserve/writer.py`        |
| `audit`             | Audit trail events                | migrated from PG (2026-04-22)  |
| `api-usage`         | Per-request token/cost/latency    | migrated from PG (2026-04-22)  |
| `llm-calls`         | LLM call details per worktree     | `llm/client.py` `_oo_index`    |
| `intel-update-log`  | Intel feed update log entries     | `db/intel/bootstrap.py`        |

Stream naming: `cybersecsuite-<base>-YYYY.MM.DD` (daily rollover, auto-stamped by `bulk_index()`).

## Key Conventions
- **All Python package management uses `uv` only**
- All DB calls **must be async** — no sync Tortoise ORM
- Pydantic v2 for all data models
- MCP tools follow the SDK pattern in `src/csmcp/cybersec/`
- `uv run python -m csmcp.cybersec_server` — runs the MCP server
- `uv run python -m proxy.asgi` — starts ASGI server

## Docker Compose & Environment (Correct Service Names)
The entire stack runs in Docker Compose. After any code change, **restart the affected service**:

- `docker compose restart cybersec-dashboard`
- `docker compose restart cybersec-postgres`
- `docker compose restart cybersec-openobserve`
- `docker compose restart cybersec-redis`

**Key ENV Vars (from docker-compose.yml)**
```
OPENOBSERVE_HOST=http://cybersec-openobserve:5080   # or http://127.0.0.1:5080 from host
OPENOBSERVE_ORG=default
OPENOBSERVE_EMAIL=admin@cybersec.local
OPENOBSERVE_PASSWORD=cYb3rS3c!
CYBERSEC_DB_HOST=/tmp
CYBERSEC_DB_PASSWORD=change_me   # default in docker-compose; override in .env
CYBERSEC_REDIS_URL=redis://cybersec-redis:6379/0
```

## Scope Model (5 Levels — Must Follow Exactly)

**Important:** 
- Global and App scopes exist after installation.
- **Project, Runtime, and Session scopes only exist after installation** and are always located in the **present working directory** (`.css/` folder in the current project root).

| Scope       | Path                                                         | Purpose                     |
|-------------|--------------------------------------------------------------|-----------------------------|
| **Global**  | `~/.claude/`                                                 | IDE config only             |
| **App**     | `~/.cybersecsuite/`                                          | Vault + Obsidian memory     |
| **Project** | `.css/` (in present working dir after install)               | Project-specific overrides  |
| **Runtime** | `.css/<runtime-id>/` (in present working dir)                | Container/pod isolation     |
| **Session** | `.css/<runtime-id>/worktree-<SID>/` (in present working dir) | Ephemeral per-session state |

**Rule:** Add `runtime_id`, `worktree_path`, `scope_level` to every `ScopedEntry` model.

## Tool SDK Pattern
```python
@tool("tool_name", "description", {"param": {"type": "string", "description": "..."}})
async def _fn(args: dict[str, Any]) -> dict:
    return sdk_result({"key": args.get("param")})
```

## Directory Map (Key Paths)
- `src/ai_proxy/routing/combo.py` — main routing (QoL injection hook)
- `src/csmcp/cybersec/tool_toggles.py` — existing toggles (extend for QoL)
- `src/dashboard/api/` — add `qol.py` here
- `src/browser-plugin/` — Chrome extension (manifest v3)
- `src/db/models/` — all Tortoise ORM models (~41 models, PG only)
- `src/openobserve/` — OO client, writer, streams registry
- `docs/scope-model.md` and `docs/database.md` — read these first

---

**This is the only instructions file you need.**
