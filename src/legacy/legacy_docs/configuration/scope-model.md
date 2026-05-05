# Scope Model

CyberSecSuite uses a four-scope isolation model for all runtime state.

---

## The Four Scopes

| Scope     | Path                                          | Purpose                                          |
|-----------|-----------------------------------------------|--------------------------------------------------|
| **Global**  | `~/.claude/`                                | LLM harness config (Claude Code settings)        |
| **App**     | `~/.cybersecsuite/`                         | All runtime state (sessions, cache, logs, keys)  |
| **Project** | `$(pwd)/.claude/`                           | Project-specific harness config and agents       |
| **Session** | `~/.cybersecsuite/sessions/<sid>/`          | Ephemeral per-session state (auto-cleaned)       |

---

## App Home: `~/.cybersecsuite/`

Created by `python src/manage.py install`. The `CYBERSECSUITE_HOME` env var overrides the default.

```
~/.cybersecsuite/
├── sessions/           Per-session state (ephemeral)
│   └── <session-id>/
│       ├── memory/     Session-scoped memory
│       └── context/    Session context files
├── memory/             Persistent memory tiers
│   ├── system/         Global defaults (read-only baseline)
│   ├── project/        Project-level overrides
│   └── session/        Ephemeral session state (highest priority)
├── templates/          Custom prompt templates
├── cache/              Encrypted tool result cache
├── logs/               Session logs and audit trail
└── .cybersecsuite      Sentinel marker (created by install)
```

### `CYBERSECSUITE_HOME` env var

```bash
# Use a custom path instead of ~/.cybersecsuite
export CYBERSECSUITE_HOME=/opt/cybersecsuite

# Verify
python src/manage.py status
```

All runtime code resolves the app home via `get_app_home()` in `src/hooks/_utils.py`.

---

## Memory Hierarchy

Memory is resolved in priority order (highest wins):

```
~/.cybersecsuite/memory/session/   ← highest priority
       ▲
~/.cybersecsuite/memory/project/   ← project overrides
       ▲
~/.cybersecsuite/memory/system/    ← global defaults (read-only)
```

MCP tool `get_project_memory` reads from all tiers, merging with session taking precedence.

---

## Project Scope: `$(pwd)/.claude/`

Contains Claude Code-specific configuration. Not used for app state.

```
$(pwd)/.claude/
├── agents/             Agent definitions loaded for this project
├── skills/             Project-specific skill overrides
├── hooks/              Project-level hooks (filesystem subprocess hooks)
└── settings.json       Project agent + MCP config
```

See [mcp-json.md](mcp-json.md) for MCP server wiring and [env-vars.md](env-vars.md) for harness environment configuration.

---

## Scope Isolation

| Data type              | Scope               | Storage path                               |
|------------------------|---------------------|--------------------------------------------|
| Session logs           | Session             | `~/.cybersecsuite/sessions/<sid>/`         |
| Project memory         | Project             | `~/.cybersecsuite/memory/project/`         |
| Tool cache             | App                 | `~/.cybersecsuite/cache/`                  |
| Crypto keys            | App / System        | `$DYSTOPIAN_KEYS_DIR`                      |
| Vault secrets          | App                 | `~/.dystopian-crypto/vault/`               |
| Investigation findings | DB (workspace/proj) | PostgreSQL `cybersec_forensics`            |

---

## First-Run Setup

```bash
# Creates ~/.cybersecsuite/ with all required subdirectories
python src/manage.py install

# Or via Makefile
make css-first-setup
```

This is idempotent — safe to run multiple times.
