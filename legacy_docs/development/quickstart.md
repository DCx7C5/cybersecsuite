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
# Creates .env from .env.example (skips if .env already exists)
```

Open `.env` and fill in secrets:

```bash
CYBERSEC_DB_PASSWORD=your_strong_password
ANTHROPIC_API_KEY=sk-ant-...
# Optional
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
```

See [`../configuration/env-vars.md`](../configuration/env-vars.md) for the complete reference.

---

## Step 3 — Install dependencies

```bash
make install
# Runs: uv sync --all-groups
```

---

## Step 3.5 — One-time bootstrap

```bash
make css-first-setup
```

Idempotent. Creates `~/.cybersecsuite/{sessions,templates,cache,logs}` (mode `700`), patches `~/.claude/settings.json`, runs `schema` + `seed`, writes `.css-initialized` sentinel.

After this, `make serve` and `make docker-up` skip bootstrap automatically.

---

## Step 4 — Start PostgreSQL

```bash
make db
# Starts PostgreSQL container via Docker Compose
```

Or for native PostgreSQL:
```sql
CREATE USER cybersec WITH PASSWORD 'your_password';
CREATE DATABASE cybersec_forensics OWNER cybersec;
```

---

## Step 5 — Create schema and seed data

```bash
make schema    # Create all tables (idempotent)
make seed      # Seed MITRE/CVE/CWE/CAPEC intelligence
```

> First seed downloads and indexes MITRE ATT&CK, CVE, CWE, and CAPEC datasets — takes 2–5 minutes. After that, set `CYBERSEC_BOOTSTRAP_INTEL_ON_START=false`.

Verify:
```bash
make status
# Initialized : True
# Intel Seeded: True
# DB          : cybersec_forensics @ localhost:5432
```

---

## Step 6 — Start the ASGI server

```bash
make serve
# Starts uvicorn at http://127.0.0.1:8000 with --reload
```

Verify:
```bash
curl http://localhost:8000/health
# → {"status": "ok", "initialized": true, ...}
```

---

## Step 7 — Open the dashboard

```
http://localhost:8000/
```

---

## Using the MCP server

```bash
make mcp
# Starts FastMCP stdio server
```

Configure in `mcp.json` (already present in repo root). Claude Code auto-detects all 83 tools across `cybersec` (78) and `dystopian` (5) MCP servers.

---

## Using the AI proxy

```bash
# Via Makefile
make asgi-chat PROMPT="Analyze this IOC: 192.168.1.100"

# Via curl
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "auto", "messages": [{"role": "user", "content": "hello"}]}'
```

---

## Sending an A2A request

```bash
curl http://localhost:8000/.well-known/agent.json

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
# → make env install db schema seed, then make serve
```

---

## 3-step Docker start

```bash
docker compose up -d
python src/manage.py seed   # first run only
claude                       # opens Claude Code with cybersec-agent
```

---

## Next steps

- [`../architecture/overview.md`](../architecture/overview.md) — system design
- [`../configuration/env-vars.md`](../configuration/env-vars.md) — full env var reference
- [`../api/http-endpoints.md`](../api/http-endpoints.md) — REST and A2A API reference
- [`../agents/reference.md`](../agents/reference.md) — all agents
- [`../mcp/overview.md`](../mcp/overview.md) — all 83 MCP tools
- [`../agents/teams.md`](../agents/teams.md) — blue/red/purple team mode
