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

make setup
# → make env install db schema seed

# Or step by step:
make env       # create .env from .env.example
make install   # uv sync --all-groups
make db        # start PostgreSQL via Docker
make schema    # create all tables
make seed      # seed MITRE/CVE/CWE/CAPEC intelligence
```

---

## Daily Workflow

```bash
make serve     # start ASGI server (http://localhost:8000)
make test      # run all tests
make lint      # ruff lint
make fmt       # ruff format
make shell     # interactive Python shell with all models
```

---

## Adding an Agent

1. Create `.claude/agents/your-agent.md`
2. Required frontmatter:

```yaml
---
name: your-agents
description: "One-line trigger description. Invoke for: ... Triggers: ..."
model: sonnet          # haiku | sonnet | opus
maxTurns: 30
tools:
  - Read
  - Bash
disallowedTools:       # omit for dev agents, add for read-only analysts
  - Write
  - Edit
---
```

3. The agent loads automatically on next server start — no code changes needed.
4. Test routing: `@your-agent hello` via A2A

Guidelines:
- `description` must contain `Invoke for:` and `Triggers:` (used by orchestrator routing)
- Read-only analysts → add `disallowedTools: [Write, Edit, MultiEdit]`
- Developer agents → include `Write`, `Edit`, `MultiEdit` in `tools`
- Heavy reasoning tasks → `model: opus`
- Lightweight monitoring → `model: haiku`

---

## Adding an MCP Tool

1. Choose the appropriate module in `src/csmcp/cybersec/` (or create one)
2. Use the SDK decorator pattern:

```python
from csmcp.cybersec._sdk import tool, sdk_result

@tool("cybersec.your_tool", "Tool description", {
    "param": {"type": "string", "description": "..."}
})
async def _your_tool(args: dict[str, Any]) -> dict:
    value = args.get("param", "default")
    return sdk_result({"key": value})

ALL_TOOLS = [_your_tool]
```

3. Export `ALL_TOOLS` from the module and add to `src/csmcp/cybersec/__init__.py`
4. Document in [`../mcp/overview.md`](../mcp/overview.md)

---

## Adding a Database Model

1. Create `src/db/models/your_model.py` with a Tortoise `Model` class
2. Add to `src/db/models/__init__.py` exports
3. Run `make schema` (idempotent, no migrations)
4. Document in `src/db/README.md`

---

## Adding an AI Provider

1. Add a `ProviderConfig` registration in `src/ai_proxy/providers/registry.py`
2. Add a translator in `src/ai_proxy/translators/`
3. Add an executor in `src/ai_proxy/executors/`
4. Add the API key env var to `.env.example`
5. Document in `src/ai_proxy/README.md`

---

## Adding Intel Fixtures

Intel fixtures live in `src/db/fixtures/*.json`. Each file maps to a specific intel table.

**Directory:**
```
src/db/fixtures/
├── mitre_techniques.json
├── mitre_actors.json
├── mitre_software.json
├── cwes.json
├── capec_patterns.json
├── nist_csf_controls.json
└── nist_ai_rmf_controls.json
```

**Seeding commands:**

| Command | Description |
|---------|-------------|
| `python src/manage.py seed` | Seed all defaults |
| `python src/manage.py seed-intel` | Seed all intel datasets |
| `python src/manage.py seed-nist-csf` | NIST CSF controls only |
| `python src/manage.py seed-nist-ai-rmf` | NIST AI RMF controls only |
| `python src/manage.py seed-mitre` | MITRE ATT&CK techniques |
| `python src/manage.py seed-cwe` | CWE weakness enumeration |
| `python src/manage.py seed-capec` | CAPEC attack patterns |

To add a new dataset:
1. Create `src/db/fixtures/your_dataset.json`
2. Register a seed function in `src/db/seeds.py`
3. Wire to a `manage.py` command
4. Add to `seed-intel` aggregate

---

## Tests

```bash
make test              # all tests
make test-cov          # with HTML coverage report
make test-crypto       # crypto tests only
```

Tests live in `tests/`. Framework: pytest.

---

## Code Style

- **Formatter**: ruff (`make fmt`)
- **Linter**: ruff (`make lint`)
- **Type hints**: all public functions and class methods
- **Async**: prefer `async def` for all I/O-bound operations
- **Imports**: stdlib → third-party → local (ruff enforces)
- **Comments**: only where the logic is non-obvious

---

## Package Management

`uv` only — never use `pip` directly.

```bash
uv add package-name                   # add dependency
uv add --group dev package-name       # add dev dependency
uv add --group test package-name      # add test dependency
uv sync --all-groups                  # sync all groups
uv run python script.py               # run in uv env
```

---

## Commit Style

```
type: short description

Optional longer body.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

---

## Directory Conventions

| Directory         | Contents                                    |
|-------------------|---------------------------------------------|
| `src/`            | All Python source (on `PYTHONPATH`)         |
| `tests/`          | pytest test files                           |
| `docs/`           | Project documentation                       |
| `.claude/agents/` | Agent definition files                      |
| `.claude/`        | Claude Code project configuration           |
| `data/`           | Runtime data (not committed)                |
| `templates/`      | Jinja2 templates                            |
| `scripts/`        | CLI utility scripts                         |
