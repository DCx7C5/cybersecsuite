# Scope Refactor & MCP Integration Fixes — April 2026

_Last updated: 2026-04-21_

---

## Overview

This document summarises two work streams completed in the April 2026 session:

1. **Four-scope model refactor** — moved all runtime/session state out of the project tree into a dedicated app-home (`~/.cybersecsuite`)
2. **MCP integration bug fixes** — corrected the stdio server bridge, removed hardcoded developer paths, fixed async type errors

---

## 1. Four-Scope Model

### Scopes

| Scope | Path | Purpose |
|---|---|---|
| **Global** | `~/.claude/` | LLM harness config only (Claude Code) |
| **App** | `$CYBERSECSUITE_HOME` (default `~/.cybersecsuite/`) | All runtime state: sessions, memory, vault, cache, logs |
| **Project** | `$(pwd)/.claude/` | Project-level harness config (agents, hooks, skills) |
| **Session** | `$CYBERSECSUITE_HOME/sessions/<sid>/` | Per-session artifacts, findings, IOCs, timeline |

Set `CYBERSECSUITE_HOME` to override the app-home path (e.g. in tests or multi-tenant installs).

### App-home directory tree

```
~/.cybersecsuite/
├── .cybersecsuite          ← install marker (JSON: version, installed_at)
├── sessions/               ← one dir per session-id + latest/ symlink
├── memory/
│   ├── system/             ← system-wide baseline, hook logs
│   ├── project/            ← project-scoped knowledge (last_session.md, etc.)
│   └── session/            ← active session scratch space
├── vault/
│   ├── memories/           ← Obsidian memory backend
│   └── wiki/               ← Obsidian vault wiki pages
├── cache/
├── logs/
├── data/
│   ├── projects/
│   └── workspaces/
├── skills/                 ← merged skill index output
└── providers/              ← provider config overrides
```

### Creating the structure

```bash
uv run python src/manage.py install
# or override path:
CYBERSECSUITE_HOME=/opt/ccs uv run python src/manage.py install
```

Idempotent — safe to re-run. Existing directories are not modified.

---

## 2. Files Changed

### `src/hooks/_utils.py`
- Added `get_app_home()` — reads `CYBERSECSUITE_HOME` at call time (supports runtime override)
- Added `get_memory_dir(layer)` helper
- `SESSIONS_DIR` now points at `$app_home/sessions/`
- `ensure_structure()` creates the full app-home tree
- Legacy fallback: `get_session_dir()` still checks `$(pwd)/.claude/sessions/<sid>` before creating under app-home (migration bridge)

### `src/hooks/first_init.py` · `session_start.py` · `session_end.py` · `baseline_updated.py`
- All memory layer paths changed from `$(pwd)/.memory/<layer>/` → `get_app_home() / "memory" / layer`
- `session_end.py` / `session_start.py`: migrated from `loop.run_in_executor(None, fn, *args)` to `asyncio.to_thread(lambda: fn(...))` — fixes PyCharm/mypy `*tuple[str]` vs `*tuple[None|str, None|str, None|str]` type error from `Path.read_text`/`write_text` positional arg signature mismatch

### `src/csmcp/cybersec/helpers.py`
- `_get_base_dir()` default changed: `src/../data` → `~/.cybersecsuite/data`
- `CYBERSEC_AI_HOOKS_DIR` sys.path injection: removed hardcoded `/home/daen/Projects/AI` default; now opt-in only via env var

### `src/csmcp/cybersec/ai_memory.py`
- `_VAULT_PATH` default: `./data/vault` → `~/.cybersecsuite/vault`

### `src/memory/vault/manager.py` · `backends/obsidian.py` · `backends/obsidian_async.py`
- All vault path defaults updated to `~/.cybersecsuite/vault`
- `_DEFAULT_VAULT_PATH` constant defined in `obsidian.py` and imported by the async backend and manager

### `src/crypto/config.py`
- `load()` and `save()` defaults: stale `settings.json` (project root) → `.claude/settings.json`

### `src/manage/_commands.py`
- Added `install_command()` — creates full app-home directory tree, writes `.cybersecsuite` marker

### `src/manage/__init__.py`
- Imported `install_command`, registered as `"install"` in the async dispatcher
- Added usage string for `install` command

### `Makefile` — `ccs-first-setup` target
- Replaced inline `mkdir -p ~/.cybersecsuite/{sessions,templates,cache,logs}` with `uv run python src/manage.py install`
- Step numbering updated (install is now step 1)

---

## 3. MCP Integration Fixes

### Problem: `server.py` used dict subscript on a non-dict

`cybersec_server["instance"]` assumed `create_sdk_mcp_server()` returns a dict. It returns either a `McpSdkServerConfig` (real SDK) or `SdkMcpServer` (shim). Neither is subscriptable.

### Fix: `_build_mcp_server()` bridge function

`src/csmcp/cybersec/server.py` now builds a real `mcp.server.Server` by:

1. Reflecting over `cybersec_server._tools` (shim) or `_ALL_CYBERSEC_TOOLS` (real SDK)
2. Registering `list_tools()` and `call_tool()` handlers
3. Delegating `call_tool()` to `SdkMcpServer.call_tool()` which dispatches to the `@tool`-decorated functions

```
mcp.json (stdio)
    → mcp.server.Server   (server.py: _build_mcp_server)
        → SdkMcpServer.call_tool()   (_sdk_compat.py)
            → @tool-decorated async fn   (cybersec/*.py)
```

The same `SdkMcpServer` instance is also used in-process by `agent_sdk.py` via `ClaudeAgentOptions(mcp_servers={"cybersec": cybersec_server})` — both paths share tool logic with no duplication.

### Other fixes

| File | Bug | Fix |
|---|---|---|
| `server.py` | `logging` not imported, `main()` crashed on `logging.basicConfig()` | Added `import logging` |
| `agent_sdk.py` | Hardcoded `/home/daen/Projects/AI` as default for `_AI_HOOKS_DIR` | Opt-in via env var only |
| `agent_sdk.py` | `captured` variable potentially unbound after the `async for` loop | Initialised to `None` before the loop |

---

## 4. SDK Choice: `claude_agent_sdk` vs `anthropic`

**Keep `claude_agent_sdk`.**

| Feature | `anthropic` SDK | `claude_agent_sdk` |
|---|---|---|
| Raw API (messages, streaming) | ✅ | wraps it |
| Tool use loop | manual | ✅ managed |
| MCP server wiring | ✗ manual bridge needed | ✅ `mcp_servers=` param |
| Agent definitions | ✗ | ✅ `AgentDefinition` |
| Session continuity | manual | ✅ `resume=` |
| Multi-provider routing | ✗ (Anthropic only) | ✅ via `ANTHROPIC_BASE_URL` proxy |

The `anthropic` SDK is richer for low-level control (prompt caching, extended thinking, raw streaming). `claude_agent_sdk` is the correct layer for orchestrating MCP-tool-using agents. This project uses both: `anthropic` SDK via the AI proxy, `claude_agent_sdk` for agent dispatch.

---

## 5. Why Keep `.claude/` in the Project?

`.claude/` is **harness config only** — it should stay in the repo:

- `agents/*.md` — agent personas and tool lists (version-controlled)  
- `skills/*.md` — skill taxonomy (version-controlled)  
- `hooks/` — Claude Code hook scripts (version-controlled)  
- `settings.json` — harness defaults (version-controlled, no secrets)
- `settings.local.json` — local overrides (gitignored)

**Not** in `.claude/`: sessions, memory, vault, logs, cache. Those all live in `~/.cybersecsuite/`.
