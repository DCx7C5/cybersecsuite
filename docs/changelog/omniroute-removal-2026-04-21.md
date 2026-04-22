# OmniRoute References Removed — 2026-04-21

Deleted all OmniRoute references from docs and source. The TypeScript OmniRoute MCP server
(`src/omniroute_mcp/`) and its Python stub counterpart (`routing.py`) were already removed.
This change cleans up the remaining traces.

## Changes

### Deleted
- `docs/mcp/omniroute-tools.md`

### Docs updated
- `docs/README.md` — tool totals: 110 → 83 (78 cybersec + 5 dystopian)
- `docs/mcp/overview.md` — server table: 3 servers → 2 servers, totals updated
- `docs/mcp/tools.md` — removed omniroute link
- `docs/architecture/overview.md` — removed omniroute tree entry and port row (20128)
- `docs/architecture/module-map.md` — removed `omniroute_mcp/` entry
- `docs/configuration/env-vars.md` — removed OmniRoute MCP section and port row
- `docs/configuration/mcp-json.md` — removed omniroute server entry from JSON and tables
- `docs/development/quickstart.md` — updated tool counts

### Source updated (comments/paths only)
- `src/proxy/asgi.py` — TLS cert/key default paths: `~/.omniroute/` → `~/.cybersecsuite/`
- `src/crypto/README.md` — key/cert paths: `~/.omniroute/` → `~/.cybersecsuite/`
- `src/ai_proxy/providers/registry.py`, `executors/base.py`, `translators/core.py`, `routing/combo.py`, `services/rate_limiter.py` — removed "Mirrors OmniRoute's ..." from module docstrings
- `src/csmcp/cybersec/proxy.py` — removed OmniRoute reference from docstring and error message

---

# Dystopian Server Merged into Cybersec — 2026-04-21

The separate `dystopian-crypto` MCP server has been merged into `cybersec`. Tool count: 78 → **83**.

## Changes

- `src/csmcp/cybersec/__init__.py` — imports and appends `_ALL_DYSTOPIAN_TOOLS` from `dystopian.py`
- `src/csmcp/__init__.py` — `all_servers()` returns only `{"cybersec"}`, `allowed_tools()` uses single list
- `src/csmcp/cybersec/tool_search.py` — removed separate dystopian import; tools already in `_ALL_CYBERSEC_TOOLS`
- `src/a2a/agent_sdk.py` — updated comments (36 → 83, removed dystopian references)
- `mcp.json` — `dystopian-crypto` entry deleted; `DYSTOPIAN_KEYS_DIR` + `DYSTOPIAN_VAULT_PASSWORD_FILE` moved into `cybersec` env; description updated
- `docs/mcp/overview.md` — one server, prefix `mcp__cybersec__*` only
- `docs/mcp/dystopian-tools.md` — updated server name and entry point
- `docs/README.md` — counts updated

Tool prefix change: `mcp__dystopian__crypto_*` → `mcp__cybersec__crypto_*`

---

## src/ README Integration — 2026-05

Moved 6 src/ component READMEs into docs/. Deleted stale `src/csmcp/README.md` (Phase A planning doc).

| Source | Destination |
|--------|-------------|
| `src/a2a/README.md` | `docs/api/a2a-protocol.md` (replaced) |
| `src/ai_proxy/README.md` | `docs/architecture/ai-proxy.md` (new) |
| `src/crypto/README.md` | `docs/development/crypto.md` (new) |
| `src/dashboard/README.md` | `docs/api/dashboard.md` (new) |
| `src/db/README.md` | `docs/development/database.md` (new) |
| `src/proxy/README.md` | `docs/architecture/asgi-proxy.md` (new) |

- Fixed stale link `docs/agent-sdk-integration.md` → `docs/agents/sdk-integration.md`
- Fixed stale tool count 29 → 83 in dashboard.md
- `docs/README.md` updated with all 6 new entries
