# Quickstart

Get CyberSecSuite running from scratch in under 10 minutes.

## Prerequisites

| Requirement | Version | Install                                               |
|-------------|---------|-------------------------------------------------------|
| Python      | 3.14+   | [python.org](https://python.org) or pyenv             |
| uv          | latest  | `curl -LsSf https://astral.sh/uv/install.sh \| sh`    |
| PostgreSQL  | 15+     | Docker (recommended) or native                        |
| Docker      | 24+     | [docker.com](https://docker.com) — only for `make db` |

At minimum, you need `ANTHROPIC_API_KEY` for agent execution. Other provider keys are optional.

---

## Step 1 — Clone and enter the repo

```bash
git clone https://github.com/yourorg/cybersecsuite
cd cybersecsuite
```

---

## Step 2 — Create your `.env` file

```bash
make env
# → Creates .env from .env.example (skips if .env already exists)
```

Open `.env` and fill in your secrets:

```bash
# Required
CYBERSEC_DB_PASSWORD=your_strong_password

# Required for AI agents
ANTHROPIC_API_KEY=sk-ant-...

# Optional — add any providers you have keys for
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
GROQ_API_KEY=...
```

See [configuration.md](configuration.md) for the complete env var reference.

---

## Step 3 — Install dependencies

```bash
make install
# Runs: uv sync --all-groups
```

---

## Step 4 — Start PostgreSQL

If you have Docker:

```bash
make db
# Starts PostgreSQL container (cybersec-postgres) via Docker Compose
```

If you have a native PostgreSQL install, create the database manually:

```sql
CREATE USER cybersec WITH PASSWORD 'your_password';
CREATE DATABASE cybersec_forensics OWNER cybersec;
```

---

## Step 5 — Create schema and seed data

```bash
make schema    # Create all 50 tables (idempotent — safe to re-run)
make seed      # Seed defaults + bootstrap MITRE/CVE/CWE intelligence
```

> The `seed` command downloads and indexes MITRE ATT&CK, CVE, CWE, and CAPEC datasets. This takes 2–5 minutes on the first run. After that, set `CYBERSEC_BOOTSTRAP_INTEL_ON_START=false` in `.env`.

Check the database is healthy:

```bash
make status
```

Expected output:
```
Initialized : True
Intel Seeded: True
DB          : cybersec_forensics @ localhost:5432
```

---

## Step 6 — Start the ASGI server

```bash
make serve
# Starts uvicorn at http://127.0.0.1:8000 with --reload
```

Verify it's running:

```bash
curl http://localhost:8000/health
# → {"status": "ok", "initialized": true, ...}
```

---

## Step 7 — Open the dashboard

```
http://localhost:8000/dashboard/
```

Or generate a static dashboard HTML:

```bash
make dashboard
# → skills/dashboard/index.html

make dashboard-serve
# → serves at http://localhost:9000
```

---

## Using the MCP server

For Claude Desktop or Claude Code, start the MCP server in a separate terminal:

```bash
make mcp
# Starts FastMCP stdio server with 29 cybersec tools
# Dystopian MCP server provides 5 additional crypto tools (mcp__dystopian__*)
```

Configure in `mcp.json` (already present in repo root). Claude will automatically detect and use all 65 tools across the `cybersec`, `dystopian`, and `omniroute` MCP servers.

---

## Using the AI proxy

The `/v1/*` endpoint is OpenAI-compatible. Point any OpenAI SDK at it:

```bash
# Via Makefile
make proxy-chat PROMPT="Analyze this IOC: 192.168.1.100"

# Via curl
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "auto", "messages": [{"role": "user", "content": "hello"}]}'
```

---

## Sending an A2A request

```bash
# Discover the agent card
curl http://localhost:8000/.well-known/agent.json

# Send a task to the orchestrator
curl -X POST http://localhost:8000/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tasks/send",
    "id": 1,
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "@cybersec-analyst CVE-2024-1234"}]
      }
    }
  }'
```

---

## One-command alternative

```bash
make setup
# Runs: make env install db schema seed
# Then: make serve
```

This is the fastest path for a fresh developer machine with Docker available.

---

## 3-step quick start (Docker)

If you have Docker and your `.env` ready:

```bash
# 1. Start all services (PostgreSQL, Redis, dashboard)
docker compose up -d

# 2. Seed intelligence databases (first run only)
python src/manage.py seed

# 3. Open Claude Code with cybersec-agent as orchestrator
claude
```

---

## Next steps

- [architecture.md](architecture.md) — understand the system design
- [configuration.md](configuration.md) — full env var reference
- [api.md](api.md) — REST and A2A API reference
- [agents.md](agents.md) — all 33 available agents
- [mcp-tools.md](mcp-tools.md) — all 65 MCP tools (31 cybersec + 5 dystopian + 29 omniroute)
- [teams.md](teams.md) — blue/red/purple team mode
