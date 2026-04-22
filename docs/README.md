# CyberSecSuite Documentation

Full documentation index for CyberSecSuite — a full-stack cybersecurity forensics platform.

---

## Architecture

| Document                                                   | Description                                                     |
|------------------------------------------------------------|-----------------------------------------------------------------|
| [`architecture/asgi-proxy.md`](architecture/asgi-proxy.md) | ASGI app: mounts, TLS, startup/shutdown                         |
| [`architecture/ai-proxy.md`](architecture/ai-proxy.md)     | AI proxy: providers, routing strategies, circuit breaker        |
| [`architecture/overview.md`](architecture/overview.md)     | System overview: 7-layer model, services, ports, docker compose |
| [`architecture/module-map.md`](architecture/module-map.md) | Full `src/` directory tree, all 24 MCP modules, DB models       |
| [`architecture/data-flow.md`](architecture/data-flow.md)   | Request flows, hooks pipeline, memory hierarchy                 |

---

## Configuration

| Document                                                       | Description                                            |
|----------------------------------------------------------------|--------------------------------------------------------|
| [`configuration/env-vars.md`](configuration/env-vars.md)       | All environment variables with defaults                |
| [`configuration/scope-model.md`](configuration/scope-model.md) | Four-scope model, `~/.cybersecsuite/` directory layout |
| [`configuration/mcp-json.md`](configuration/mcp-json.md)       | `mcp.json` reference, tool counts per server           |

---

## MCP Tools (83)

| Document                                           | Description                                    |
|----------------------------------------------------|------------------------------------------------|
| [`mcp/overview.md`](mcp/overview.md)               | All 83 tools in cybersec server                |
| [`mcp/dystopian-tools.md`](mcp/dystopian-tools.md) | 5 crypto tools: Ed25519, Argon2id, AES-256-GCM |
| 
---

## Agents

| Document                                                 | Description                                            |
|----------------------------------------------------------|--------------------------------------------------------|
| [`agents/reference.md`](agents/reference.md)             | All 18 active agent files + 33-agent spec roster       |
| [`agents/teams.md`](agents/teams.md)                     | Blue/red/purple team compositions                      |
| [`agents/sdk-integration.md`](agents/sdk-integration.md) | SDK flow, model routing, caching, hooks, MCP injection |

---

## API Reference

| Document                                         | Description                                            |
|--------------------------------------------------|--------------------------------------------------------|
| [`api/http-endpoints.md`](api/http-endpoints.md) | All HTTP endpoints: health, `/v1/`, `/api/*`, `/sse/*` |
| [`api/dashboard.md`](api/dashboard.md)           | Dashboard REST + SSE endpoints                         |
| [`api/a2a-protocol.md`](api/a2a-protocol.md)     | A2A JSON-RPC methods, streaming, routing, error codes  |

---

## Deployment

| Document                                       | Description                                        |
|------------------------------------------------|----------------------------------------------------|
| [`deployment/docker.md`](deployment/docker.md) | Docker Compose services, TLS, production checklist |

---

## Development

| Document                                                     | Description                                               |
|--------------------------------------------------------------|-----------------------------------------------------------|
| [`development/crypto.md`](development/crypto.md)             | Crypto: Ed25519, BLAKE2b, Argon2id, AES-256-GCM           |
| [`development/database.md`](development/database.md)         | DB lifecycle: schema, seeds, backup, ORM models           |
| [`development/frontend.md`](development/frontend.md)         | React SPA: dev server, panels, data hooks, theming, build |
| [`development/quickstart.md`](development/quickstart.md)     | Get running from scratch in under 10 minutes              |
| [`development/contributing.md`](development/contributing.md) | Dev workflow, adding agents/tools/models/fixtures         |

---

## Changelog

| Document                                                                                       | Description                                                      |
|------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| [`changelog/react-migration-2026-04-22.md`](changelog/react-migration-2026-04-22.md)           | React 19 + TypeScript SPA migration — 56 files, 34 panels        |
| [`changelog/ts-migration-2026-04-22.md`](changelog/ts-migration-2026-04-22.md)                 | TypeScript migration: tsc as source of truth for JS              |
| [`changelog/qol-output-controls-2026-04-22.md`](changelog/qol-output-controls-2026-04-22.md)   | QoL output controls: per-agent toggle system                     |
| [`changelog/omniroute-removal-2026-04-21.md`](changelog/omniroute-removal-2026-04-21.md)       | OmniRoute removal, routing strategy consolidation                |
| [`changelog/scope-refactor-2026-04.md`](changelog/scope-refactor-2026-04.md)                   | Scope model refactor: runtime state moved to `~/.cybersecsuite/` |

---

## Quick Facts

| Item               | Value                                      |
|--------------------|--------------------------------------------|
| MCP tools          | 83 (single cybersec server)                |
| Active agents      | 18 files (33 in spec)                      |
| DB models          | 44+ Tortoise ORM models                    |
| AI providers       | 9 (60+ models)                             |
| Routing strategies | 13                                         |
| HTTP port          | 8000                                       |
| TLS port           | 8443                                       |
| Alt HTTP port      | 8765                                       |
| Observability      | OpenObserve on 5080                        |
| Frontend           | React 19 + TypeScript + Vite 8 (34 panels) |
