# Contributing

Development workflow for CyberSecSuite.

---

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) — only package manager used (no pip, no conda)
- PostgreSQL 15+ (or Docker for `make db`)
- `ANTHROPIC_API_KEY` for agent integration tests

---

## Setup

```bash
git clone https://github.com/yourorg/cybersecsuite
cd cybersecsuite

# Full setup (one command)
make setup
# → make env install db schema seed

# Or step by step
make env       # create .env from .env.example
make install   # uv sync --all-groups
make db        # start PostgreSQL via Docker
make schema    # create all 50 tables
make seed      # seed defaults + MITRE/CVE/CWE intel
```

---

## Daily workflow

```bash
# Start the server
make serve

# Run tests
make test

# Lint
make lint

# Auto-format
make fmt

# Interactive Python shell with all models
make shell
```

---

## Adding a new agent

1. Create `.claude/agents/your-agent.md`
2. Required frontmatter:

```yaml
---
name: your-agent
description: "One-line trigger description for routing. Invoke for: ..."
model: sonnet          # haiku | sonnet | opus
maxTurns: 30
tools:
  - Read
  - Bash
disallowedTools:       # omit for dev agents, add for read-only analysts
  - Write
  - Edit
---

Your agent system prompt here...
```

3. The agent loads automatically at next server start (no code changes needed)
4. Test routing: `@your-agent hello` via A2A

Guidelines:
- **description** must contain `Invoke for:` and `Triggers:` clauses (used by orchestrator routing)
- Analysts that only read evidence → add `disallowedTools: [Write, Edit, MultiEdit]`
- Developer agents → include `Write`, `Edit`, `MultiEdit` in `tools`
- Heavy reasoning (reverse engineering, firmware) → `model: opus`
- Lightweight monitoring → `model: haiku`

---

## Adding an MCP tool

> ⚠️ Phase A (in-process MCP package) is not yet complete. For now, add tools to `mcp_server.py`.

1. Add `@mcp.tool(name="cybersec.your_tool")` in `mcp_server.py`
2. Use the helper types: `JsonDict`, `ScopeState`
3. Return format (required):
```python
return {"content": [{"type": "text", "text": json.dumps(result)}]}
```
4. Document in `docs/mcp-tools.md`

When Phase A is complete, tools will move to `src/mcp/cybersec.py`.

---

## Adding a database model

1. Create `src/db/models/your_model.py` with a `Model` class
2. Add to `src/db/models/__init__.py` exports
3. Run `make schema` to create the table (idempotent, no migrations)
4. Document in `src/db/README.md` model reference table

---

## Adding an AI provider

1. Add a `ProviderConfig` registration call in `src/ai_proxy/providers/registry.py`
2. Add a translator in `src/ai_proxy/translators/`
3. Add an executor in `src/ai_proxy/executors/`
4. Add the API key env var to `.env.example`
5. Document in `src/ai_proxy/README.md`

---

## Testing

```bash
make test              # all tests
make test-cov          # with HTML coverage report
make test-crypto       # crypto tests only
```

Tests live in `tests/`. Use pytest. No test source files exist yet (Phase B).

---

## Code style

- **Formatter**: ruff (`make fmt`)
- **Linter**: ruff (`make lint`)
- **Type hints**: all public functions and class methods
- **Docstrings**: module-level only (no per-function docstrings unless the logic is non-obvious)
- **Comments**: only where the code itself is unclear
- **Async**: prefer `async def` for all I/O-bound operations
- **Imports**: stdlib first, then third-party, then local (ruff enforces)

---

## Package management

**uv only** — never use pip directly.

```bash
# Add a dependency
uv add package-name

# Add a dev dependency
uv add --group dev package-name

# Add a test dependency
uv add --group test package-name

# Sync all groups
uv sync --all-groups

# Run a command in the uv environment
uv run python script.py
```

---

## Commit style

```
type: short description

Optional longer body.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

---

## Directory conventions

| Directory | Contents |
|-----------|---------|
| `src/` | All Python source — must be on `PYTHONPATH` |
| `tests/` | pytest test files |
| `docs/` | Project-level documentation |
| `mcps/` | External MCP server packages |
| `.claude/agents/` | Claude agent definitions |
| `.claude/` | Claude Code project config |
| `data/` | Runtime data (not committed) |
| `templates/` | Jinja2 templates |
