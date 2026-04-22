# Environment Variables Reference

Complete reference for all environment variables and settings.

---

## PostgreSQL

| Variable               | Default              | Description           |
|------------------------|----------------------|-----------------------|
| `CYBERSEC_DB_HOST`     | `localhost`          | PostgreSQL host       |
| `CYBERSEC_DB_PORT`     | `5432`               | PostgreSQL port       |
| `CYBERSEC_DB_USER`     | `cybersec`           | Database user         |
| `CYBERSEC_DB_PASSWORD` | *(required)*         | Database password     |
| `CYBERSEC_DB_NAME`     | `cybersec_forensics` | Database name         |

## Redis

| Variable    | Default                  | Description                                      |
|-------------|--------------------------|--------------------------------------------------|
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL (rate limiter, token cache) |

## Startup Behaviour

| Variable                            | Default | Description                                                        |
|-------------------------------------|---------|--------------------------------------------------------------------|
| `CYBERSEC_AUTO_CREATE_DB`           | `true`  | Create DB + schema on startup (safe/idempotent)                    |
| `CYBERSEC_BOOTSTRAP_INTEL_ON_START` | `false` | Load MITRE/CVE/CWE intel at startup (slow — run once then disable) |

## App Home & Scope

| Variable              | Default             | Description                                           |
|-----------------------|---------------------|-------------------------------------------------------|
| `CYBERSECSUITE_HOME`  | `~/.cybersecsuite`  | App home directory (sessions, cache, templates, logs) |
| `CYBERSEC_WORKSPACE`  | `default`           | Default workspace name                                |
| `CYBERSEC_PROJECT`    | `default`           | Default project name                                  |
| `CYBERSEC_SESSION_ID` | *(unset)*           | Session ID (optional, set per investigation)          |

Run `python src/manage.py install` to create `~/.cybersecsuite/` with all required subdirectories.

See [scope-model.md](scope-model.md) for the full four-scope model.

## Data Directories

| Variable               | Default                               | Description                 |
|------------------------|---------------------------------------|-----------------------------|
| `CYBERSEC_BASE_DIR`    | `./data`                              | Root data directory         |
| `CYBERSEC_INTEL_DIR`   | `./data/cybersec-shared/intelligence` | Shared intelligence cache   |
| `CYBERSEC_PROJECT_DIR` | `.`                                   | Current project root        |

## ASGI / Ports

| Variable        | Default | Description                                   |
|-----------------|---------|-----------------------------------------------|
| `ASGI_HOST`     | `0.0.0.0` | Bind address                                |
| `ASGI_PORT`     | `8000`  | Primary HTTP port                             |
| `ASGI_TLS_PORT` | `8443`  | HTTPS port (when TLS configured)              |
| `ASGI_TLS_CERT` | *(unset)* | TLS certificate path (activates TLS when set) |
| `ASGI_TLS_KEY`  | *(unset)* | TLS private key path                          |

TLS activates automatically when both `ASGI_TLS_CERT` and `ASGI_TLS_KEY` are set. Generate keys:
```bash
python src/manage.py ssl-genkey
```

## A2A Server

| Variable                | Default                 | Description                                       |
|-------------------------|-------------------------|---------------------------------------------------|
| `CYBERSEC_A2A_BASE_URL` | `http://localhost:8000` | Base URL for agent card URLs + inter-agent calls  |
| `CYBERSEC_A2A_PORT`     | `8000`                  | A2A listening port (informational)                |

## AI Provider API Keys

| Variable             | Provider                               |
|----------------------|----------------------------------------|
| `ANTHROPIC_API_KEY`  | Anthropic Claude (required for agents) |
| `OPENAI_API_KEY`     | OpenAI                                 |
| `GEMINI_API_KEY`     | Google Gemini                          |
| `GROQ_API_KEY`       | Groq                                   |
| `DEEPSEEK_API_KEY`   | DeepSeek                               |
| `MISTRAL_API_KEY`    | Mistral                                |
| `XAI_API_KEY`        | xAI Grok                               |
| `TOGETHER_API_KEY`   | Together AI                            |
| `OPENROUTER_API_KEY` | OpenRouter                             |

## OpenObserve (Observability)

| Variable                  | Default                         | Description                        |
|---------------------------|---------------------------------|------------------------------------|
| `OPENOBSERVE_HOST`        | `http://localhost:5080`         | OpenObserve base URL               |
| `OPENOBSERVE_ORG`         | `default`                       | OpenObserve organisation           |
| `OPENOBSERVE_ROOT_EMAIL`  | `admin@cybersec.local`          | Admin email                        |
| `OPENOBSERVE_ROOT_PASSWORD` | *(required)*                  | Admin password                     |

Start with `docker-compose up -d cybersec-openobserve`.

## Crypto

| Variable             | Default                             | Description            |
|----------------------|-------------------------------------|------------------------|
| `DYSTOPIAN_KEYS_DIR` | `/etc/dystopian/crypto/cert/private` | Ed25519 key storage   |
| `DYSTOPIAN_VAULT_PASSWORD` | *(required)*                  | Vault encryption password |

## Debug

| Variable | Default | Description                                           |
|----------|---------|-------------------------------------------------------|
| `DEBUG`  | `false` | Enable Starlette debug mode (never use in production) |

---

## Port Reference

| Port    | Protocol | Service                        | Env var                         |
|---------|----------|--------------------------------|---------------------------------|
| `8000`  | HTTP     | ASGI server (primary)          | `ASGI_PORT`                     |
| `8443`  | HTTPS    | TLS proxy                      | `ASGI_TLS_PORT`                 |
| `8765`  | HTTP     | Alt HTTP (Docker Compose)      | —                               |
| `5432`  | TCP      | PostgreSQL                     | `CYBERSEC_DB_PORT`              |
| `6379`  | TCP      | Redis                          | `REDIS_URL`                     |
| `5080`  | HTTP     | OpenObserve                    | `OPENOBSERVE_HOST`              |
| `11434` | HTTP     | Ollama (local LLM)             | —                               |

---

## Production Checklist

- `DEBUG=false`
- Strong `CYBERSEC_DB_PASSWORD` (not `change_me`)
- `CYBERSEC_AUTO_CREATE_DB=false` after initial setup
- `CYBERSEC_BOOTSTRAP_INTEL_ON_START=false` after first seed
- TLS cert configured (`ASGI_TLS_CERT` + `ASGI_TLS_KEY`)
- All required API keys set
- `.env` has permissions `600` (`chmod 600 .env`)
