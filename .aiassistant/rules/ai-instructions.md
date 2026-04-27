---
apply: always
---

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

- `docker compose restart cybersec-proxy`
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


## Additional Python and TypeScript Rules
- Every new or edited Python file has to be linted with `ruff` and pass with zero errors; run `uv run ruff check <file>` to verify
- Every new or edited TypeScript file has to be linted with `eslint` and pass with zero errors; run `uv run eslint <file>` to verify
- All non exit Python Exceptions should use `Exception(BaseException)` pattern and include detailed error messages; avoid bare `except:` blocks and never use `except Exception:` without re-raising or logging the error details
- All TypeScript code must pass `tsc` with zero errors
- Use `uv` for all Python package management and script execution; do not use `pip` or `poetry` directly
- All MCP tools must follow the SDK pattern and be registered in `src/csmcp/cybersec/__init__.py`
- All database interactions must be async and use Tortoise ORM; do not use synchronous DB calls
- All LLM calls must be routed through the AI proxy and logged to OpenObserve with the `_oo_index()` helper
- All new OpenObserve streams must be registered in `src/openobserve/streams.py` and follow the naming convention `cybersecsuite-<base>-YYYY.MM.DD`
- All new agents must follow the frontmatter schema and be added to the routing logic in `src/ai_proxy/routing/combo.py` if necessary
- All new API endpoints must be added to the ASGI server in `src/proxy/asgi.py` and follow the existing patterns for request handling and OpenObserve logging
- All new features must include appropriate unit tests and integration tests, and be documented in the relevant sections of the documentation (e.g., new MCP tools in `tools.md`, new agents in `reference.md`, etc.)
- We never under any circumstances use `Any` in type annotations without a very good reason (Python & TypeScript) — prefer more specific types; or `TypedDict` for structured data; or `Protocol` for interfaces; or `TypeVar` for generics.
- All code must be well-documented with docstrings and comments where necessary, following the existing style in the codebase.
- Never use `Exception` or catch broad exceptions without re-raising or logging the error details; always use specific exception types and include error handling logic that provides useful feedback for debugging.
- Check Python for PEP 8 compliance and TypeScript for best practices; avoid antipatterns and ensure code readability and maintainability.
- Imports should be organized with standard library imports first, followed by third-party imports, and then local application imports, each separated by a blank line.
- TypeScript files must be linted with `eslint` to maintain code quality and consistency across the codebase.
---

## Documentation and Changelog
- All new features, changes, and fixes must be documented in the `docs/` directory with clear explanations, usage instructions, and examples where applicable.
- The changelog must be updated after every task list, following the format in `docs/changelog/` and including all relevant details about new features, bug fixes, and any breaking changes.


**This is the only instructions file you need.**
