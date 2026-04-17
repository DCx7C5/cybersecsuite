# Configuration Reference

Complete reference for all environment variables and settings.

---

## Environment Variables (`.env`)

Copy `.env.example` to `.env` and fill in secrets:

```bash
cp .env.example .env && chmod 600 .env
```

### Redis

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL (used by token optimizer, rate limiter) |

### PostgreSQL

| Variable | Default | Description |
|----------|---------|-------------|
| `CYBERSEC_DB_HOST` | `localhost` | PostgreSQL host |
| `CYBERSEC_DB_PORT` | `5432` | PostgreSQL port |
| `CYBERSEC_DB_USER` | `cybersec` | Database user |
| `CYBERSEC_DB_PASSWORD` | *(required)* | Database password |
| `CYBERSEC_DB_NAME` | `cybersec_forensics` | Database name |

### Startup behaviour

| Variable | Default | Description |
|----------|---------|-------------|
| `CYBERSEC_AUTO_CREATE_DB` | `true` | Create DB + schema on startup (safe/idempotent) |
| `CYBERSEC_BOOTSTRAP_INTEL_ON_START` | `false` | Load MITRE/CVE/CWE intel at startup (slow — run once then disable) |

### Data directories

| Variable | Default | Description |
|----------|---------|-------------|
| `CYBERSEC_BASE_DIR` | `./data` | Root data directory |
| `CYBERSEC_INTEL_DIR` | `./data/cybersec-shared/intelligence` | Shared intelligence cache |
| `CYBERSEC_PROJECT_DIR` | `.` | Current project root (for scope resolution) |

### Scope defaults

| Variable | Default | Description |
|----------|---------|-------------|
| `CYBERSEC_WORKSPACE` | `default` | Default workspace name |
| `CYBERSEC_PROJECT` | `default` | Default project name |
| `CYBERSEC_SESSION_ID` | *(unset)* | Optional session ID (set per investigation) |

### A2A server

| Variable | Default | Description |
|----------|---------|-------------|
| `CYBERSEC_A2A_BASE_URL` | `http://localhost:8000` | Base URL for agent card URLs + inter-agent calls |
| `CYBERSEC_A2A_PORT` | `8000` | A2A listening port (informational) |

### ASGI / ports

| Variable | Default | Description |
|----------|---------|-------------|
| `ASGI_HOST` | `0.0.0.0` | Bind address |
| `ASGI_PORT` | `8000` | Primary HTTP port |
| `ASGI_TLS_PORT` | `8433` | HTTPS port (when TLS configured) |
| `ASGI_TLS_CERT` | `~/.omniroute/certs/cert.pem` | TLS certificate path |
| `ASGI_TLS_KEY` | `~/.omniroute/certs/key.pem` | TLS private key path |

TLS activates automatically when both `ASGI_TLS_CERT` and `ASGI_TLS_KEY` exist. Generate keys with `python src/manage.py ssl-genkey`.

### AI provider API keys

| Variable | Provider |
|----------|---------|
| `ANTHROPIC_API_KEY` | Anthropic Claude (required for agents) |
| `OPENAI_API_KEY` | OpenAI |
| `GEMINI_API_KEY` | Google Gemini |
| `GROQ_API_KEY` | Groq |
| `DEEPSEEK_API_KEY` | DeepSeek |
| `MISTRAL_API_KEY` | Mistral |
| `XAI_API_KEY` | xAI Grok |
| `TOGETHER_API_KEY` | Together AI |
| `OPENROUTER_API_KEY` | OpenRouter |

### Debug

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable Starlette debug mode (never use in production) |

---

## Port Reference

| Port | Protocol | Service | Env var |
|------|----------|---------|---------|
| `8000` | HTTP | ASGI server (primary) | `ASGI_PORT` |
| `8080` | HTTP | Alt HTTP (Docker Compose) | — |
| `8433` | HTTPS | TLS proxy | `ASGI_TLS_PORT` |
| `5432` | TCP | PostgreSQL | `CYBERSEC_DB_PORT` |
| `6379` | TCP | Redis | `REDIS_URL` |
| `9000` | HTTP | Dashboard static server (make dashboard-serve) | — |

---

## `.claude/settings.json`

This is the Claude Code project settings file — separate from any application config.

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "agent": "cybersec-agent",
  "asgi": {
    "host": "0.0.0.0",
    "port": 8000,
    "alt_port": 8080,
    "tls_port": 8433,
    "tls_cert": "~/.omniroute/certs/cert.pem",
    "tls_key": "~/.omniroute/certs/key.pem"
  },
  "mcp": {
    "servers": ["cybersec", "dystopian"],
    "tool_prefix": "mcp__"
  }
}
```

### Key settings

| Key | Value | Description |
|-----|-------|-------------|
| `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `"1"` | Enables Claude Code experimental team mode. Allows agent team definitions in `.claude/agents/teams/` (blue-team.md, red-team.md, purple-team.md) to be used for multi-agent coordination. See [teams.md](teams.md). |
| `agent` | `"cybersec-agent"` | Default orchestrator agent for the project |
| `mcp.servers` | `["cybersec", "dystopian"]` | MCP servers active in this project |

This file is read by Claude Code for project-level context. It does **not** affect the running application — use environment variables for application config.

---

## `mcp.json`

Configures MCP servers available to Claude:

```json
{
  "mcpServers": {
    "cybersec": {
      "command": "uv",
      "args": ["run", "python", "mcp_server.py"],
      "env": { "PYTHONPATH": "src" }
    }
  }
}
```

Additional servers in `mcps/`:
- `mcps/playwright-stealth-mcp/` — browser automation
- `mcps/token-optimization-mcp/` — token caching + compression

---

## Uvicorn / Makefile overrides

```bash
# Override server host and port
UVICORN_HOST=0.0.0.0 UVICORN_PORT=9000 make serve

# Override PYTHONPATH
PYTHONPATH=src make serve
```

---

## Production checklist

- `DEBUG=false`
- Strong `CYBERSEC_DB_PASSWORD` (not `change_me`)
- `CYBERSEC_AUTO_CREATE_DB=false` after initial setup
- `CYBERSEC_BOOTSTRAP_INTEL_ON_START=false` after first seed
- TLS cert configured (`ASGI_TLS_CERT` + `ASGI_TLS_KEY`)
- All API keys set for providers in use
- `.env` has permissions `600` (`chmod 600 .env`)

See [deployment.md](deployment.md) for the full production deployment guide.
