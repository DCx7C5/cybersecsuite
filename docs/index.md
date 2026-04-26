# CyberSecSuite Documentation Index

## 📚 Core Documentation

- **[readme.md](readme.md)** — Full documentation overview
- **[database.md](database.md)** — Database schema and models

## 🏗️ Architecture

- **[architecture/scope-architecture.md](architecture/scope-architecture.md)** — 5-level hierarchical scope (global/app/project/runtime/session)
- **[architecture/overview.md](architecture/overview.md)** — System architecture overview
- **[architecture/ai-proxy.md](architecture/ai-proxy.md)** — AI routing and proxy layer
- **[architecture/data-flow.md](architecture/data-flow.md)** — Data flow diagrams
- **[architecture/module-map.md](architecture/module-map.md)** — Module dependencies
- **[architecture/asgi-proxy.md](architecture/asgi-proxy.md)** — ASGI gateway architecture
- **[architecture/scope-enforcement-worker-architecture.md](architecture/scope-enforcement-worker-architecture.md)** — Scope + worker integration
- **[architecture/architecture-overview.md](architecture/architecture-overview.md)** — Core architecture patterns

## 🎨 Frontend & Components

- **[features/component_patterns.md](features/component_patterns.md)** — React component patterns
- **[features/sidebar_strategy.md](features/sidebar_strategy.md)** — Sidebar layout strategy
- **[features/panel-layout-patterns.md](features/panel-layout-patterns.md)** — Panel layout patterns
- **[features/browser-plugin.md](features/browser-plugin.md)** — Browser plugin integration
- **[features/qol.md](features/qol.md)** — Quality of Life output controls

## 🔌 APIs & Integration

- **[api/http-endpoints.md](api/http-endpoints.md)** — HTTP API endpoints
- **[api/a2a-protocol.md](api/a2a-protocol.md)** — Agent-to-Agent protocol
- **[api/dashboard.md](api/dashboard.md)** — Dashboard API
- **[mcp/tools.md](mcp/tools.md)** — MCP tool registry (87 tools)
- **[mcp/overview.md](mcp/overview.md)** — MCP server overview

## 🔐 Security & Compliance

- **[audits/](audits/)** — Panel security audits (35+ detailed audits)

## 🚀 Deployment & Configuration

- **[configuration/env-vars.md](configuration/env-vars.md)** — Environment variables
- **[configuration/mcp-json.md](configuration/mcp-json.md)** — MCP configuration
- **[configuration/scope-model.md](configuration/scope-model.md)** — Scope model configuration
- **[deployment/docker.md](deployment/docker.md)** — Docker & deployment

## 👤 Agents & Teams

- **[agents/reference.md](agents/reference.md)** — Agent registry (18+ agents)
- **[agents/teams.md](agents/teams.md)** — Blue/red/purple team compositions
- **[agents/sdk-integration.md](agents/sdk-integration.md)** — SDK integration patterns

## 📋 Changelog & History

- **[changelog/index.md](changelog/index.md)** — Changelog index (phases 0–5)
- **[changelog/](changelog/)** — Individual phase changelogs (30+ files)

## 🛠️ Development

- **[development/quickstart.md](development/quickstart.md)** — Quick start guide
- **[development/database.md](development/database.md)** — Database setup & ORM
- **[development/crypto.md](development/crypto.md)** — Cryptography (Ed25519, BLAKE2b, AES)
- **[development/frontend.md](development/frontend.md)** — React SPA setup
- **[development/contributing.md](development/contributing.md)** — Contributing guidelines

## 🪝 Hooks System

- **[hooks/sessionstart.md](hooks/sessionstart.md)** — Session lifecycle
- **[hooks/rootcommandexecuted.md](hooks/rootcommandexecuted.md)** — Command execution

## 📦 Getting Started

- **[getting-started/ollama-setup.md](getting-started/ollama-setup.md)** — Ollama model setup

---

## 📊 Quick Facts

| Item | Value |
|------|-------|
| **MCP Tools** | 87 (83 cybersec + 4 QoL) |
| **Active Agents** | 18 (33 in spec) |
| **DB Models** | 44+ Tortoise ORM models |
| **AI Providers** | 9 (60+ models) |
| **Routing Strategies** | 13 |
| **QoL Toggles** | 8 (5 presets) |
| **Security Audits** | 35+ panel audits |
| **Frontend Panels** | 34 (React 19 + TypeScript) |

---

**Last Updated**: 2026-04-26  
**Total Documents**: 90+ markdown files  
**Total Size**: ~1 MB
