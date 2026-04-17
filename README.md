# CyberSecSuite

Cybersecurity forensics platform with multi-agent AI orchestration, multi-provider AI routing, 29 MCP tools, and a PostgreSQL-backed threat intelligence database.

---

## Features

- **A2A Agent Protocol** — Google Agent-to-Agent JSON-RPC 2.0 server with 32 specialist agents
- **AI Proxy** — OpenAI-compatible `/v1/*` endpoint routing across 9 providers with 13 strategies
- **29 MCP Tools** — FastMCP stdio server for Claude integration (findings, IOCs, cases, intel, routing, cache)
- **PostgreSQL Threat Intel** — 50 ORM models: MITRE ATT&CK, CVE, CWE, CAPEC, findings, IOCs, cases
- **Crypto Suite** — Ed25519 artifact signing, BLAKE2b checksums, Argon2id KDF, AES-256-GCM encryption
- **Live Dashboard** — REST + SSE monitoring UI with 16 API endpoints
- **32 Claude Agents** — Haiku/Sonnet/Opus analysts, developers, and forensics specialists

---

## Quick Start

```bash
git clone https://github.com/yourorg/cybersecsuite
cd cybersecsuite

# One-command setup (env + deps + DB + schema + seed)
make setup

# Start the ASGI server (A2A + AI proxy + dashboard)
make serve
# → http://localhost:8000

# Start the MCP server (for Claude Desktop / Claude Code)
make mcp
```

Verify it's running:
```bash
curl http://localhost:8000/health
```

See [docs/quickstart.md](docs/quickstart.md) for the full setup guide.

---

## Documentation

| Doc                                            | Description                            |
|------------------------------------------------|----------------------------------------|
| [docs/architecture.md](docs/architecture.md)   | System diagram, module map, data flows |
| [docs/quickstart.md](docs/quickstart.md)       | Full setup guide from scratch          |
| [docs/configuration.md](docs/configuration.md) | All env vars and settings              |
| [docs/api.md](docs/api.md)                     | REST + A2A API reference               |
| [docs/mcp-tools.md](docs/mcp-tools.md)         | All 29 MCP tools reference             |
| [docs/agents.md](docs/agents.md)               | All 32 agents catalog                  |
| [docs/deployment.md](docs/deployment.md)       | Docker, TLS, production setup          |
| [docs/contributing.md](docs/contributing.md)   | Development workflow                   |

### Module docs

| Module                                             | Description                   |
|----------------------------------------------------|-------------------------------|
| [src/a2a/README.md](src/a2a/README.md)             | A2A protocol implementation   |
| [src/ai_proxy/README.md](src/ai_proxy/README.md)   | Multi-provider AI routing     |
| [src/crypto/README.md](src/crypto/README.md)       | Cryptographic utilities       |
| [src/dashboard/README.md](src/dashboard/README.md) | Monitoring dashboard          |
| [src/db/README.md](src/db/README.md)               | Database layer (Tortoise ORM) |
| [src/proxy/README.md](src/proxy/README.md)         | ASGI application              |

---

## Available Commands

```
make setup          Full first-run setup
make serve          Start ASGI server (port 8000)
make mcp            Start MCP server (stdio)
make db             Start PostgreSQL via Docker
make schema         Create/update DB schema
make seed           Seed defaults + intelligence data
make status         Database status and table counts
make shell          Interactive Python shell with models
make test           Run all tests
make lint           Ruff linter
make fmt            Ruff auto-format
make dashboard      Generate static dashboard HTML
make docker-up      Start all services via Docker Compose
make proxy-chat     Chat via AI proxy CLI
```

---

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) (package manager — no pip)
- PostgreSQL 15+ (or `make db` via Docker)
- `ANTHROPIC_API_KEY` (minimum — for Claude-based agent execution)

