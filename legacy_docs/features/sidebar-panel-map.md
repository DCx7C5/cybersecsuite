# SIDEBAR-PANEL-MAP.md — Inventory of Frontend Navigation vs Backend Panels

**Last Updated:** 2026-04-26  
**Status:** Phase 1 Documentation  
**Purpose:** Map all 33 sidebar navigation items to their corresponding backend API panels/handlers

---

## Overview

This document provides a **complete inventory** of:
- **33 Sidebar navigation items** (frontend UI)
- **32 Backend dashboard API panels** (Python FastAPI handlers)
- **Mapping discrepancies** (items with no backend, backends with no frontend)

---

## Frontend Navigation Inventory

### Source: `src/frontend/src/constants/nav.ts`

**Total Sidebar Items: 33**

| # | ID | Label | Group | Frontend Status | Backend Handler | Notes |
|---|-----|------------|---------|---|---|---|
| 1 | `chat` | Chat | AGENTS | ✅ Exists | `memory_chat.py` | Core chat interface |
| 2 | `health` | Health | PLATFORM | ✅ Exists | `core.py::api_health` | System health status |
| 3 | `usage` | Usage & Cost | PLATFORM | ✅ Exists | `core.py::api_usage` | Token/cost tracking |
| 4 | `telemetry` | Telemetry | PLATFORM | ✅ Exists | `core.py` (partial) | OpenTelemetry metrics |
| 5 | `providers-hub` | Provider Hub | PLATFORM | ✅ Exists | `core.py::api_providers_hub` | Cloud provider management |
| 6 | `routing` | Routing | AI PROXY | ✅ Exists | `proxy_memory_chat.py` | AI proxy routing logic |
| 7 | `qol-controls` | QoL Controls | AI PROXY | ✅ Exists | `qol.py` + `qol_endpoints.py` | Quality-of-life toggles |
| 8 | `agent-factory` | Agent Factory | AGENTS | ✅ Exists | `agent_crud.py` | Create/modify agents |
| 9 | `agent-crafter` | Agent Crafter | AGENTS | ✅ Exists | `agents.py` | Fine-tune agent behavior |
| 10 | `team-builder` | Team Builder | AGENTS | ✅ Exists | `team_builder.py` | Multi-agent teams |
| 11 | `agent-query` | Agent Query | AGENTS | ✅ Exists | `agent_crud.py` (read) | Query agent configs |
| 12 | `workflows` | Workflows | AGENTS | ✅ Exists | `workflows.py` | Workflow orchestration |
| 13 | `flowgraph` | Flowgraph | AGENTS | ✅ Exists | `flowgraph.py` | Visual workflow DAG |
| 14 | `prompts` | Prompts | AGENTS | ✅ Exists | `prompts_crud.py` | Prompt management |
| 15 | `sdk-lab` | SDK Lab | AGENTS | ✅ Exists | `sdk_options.py` + `sdk_session.py` | SDK testing |
| 16 | `marketplace` | Marketplace | AGENTS | ✅ Exists | `marketplace.py` | Agent marketplace |
| 17 | `marketplace-factory` | Agent Factory ⊕ | AGENTS | ✅ Exists | `marketplace.py` (creation) | Marketplace agent creation |
| 18 | `cases` | Cases | OPERATIONS | ✅ Exists | `ops.py` | Investigation cases |
| 19 | `tasks` | Tasks | OPERATIONS | ✅ Exists | `ops.py` | Task management |
| 20 | `pocs` | PoCs | OPERATIONS | ✅ Exists | `ops.py` | Proof-of-concepts |
| 21 | `a2a` | A2A Proto | OPERATIONS | ✅ Exists | `a2a_crud.py` | Agent-to-Agent protocol |
| 22 | `investigations` | Investigations | FORENSICS | ✅ Exists | `forensic.py` | Forensic investigations |
| 23 | `findings` | Findings | FORENSICS | ✅ Exists | `forensic.py` | Investigation findings |
| 24 | `iocs` | IOCs | FORENSICS | ✅ Exists | `forensic.py` | Indicators of Compromise |
| 25 | `yara` | YARA Rules | FORENSICS | ✅ Exists | `forensic.py` | YARA rule management |
| 26 | `intel` | Intel Feed | FORENSICS | ✅ Exists | `intel_sources.py` | Threat intelligence |
| 27 | `audit` | Audit Log | FORENSICS | ✅ Exists | `forensic.py` (logging) | Audit trail logging |
| 28 | `compliance` | Compliance | FORENSICS | ⚠️ Component exists | ❌ No handler | **MISSING: No backend** |
| 29 | `opensearch` | OpenObserve | DATA | ✅ Exists | `openobserve_stats.py` | OpenObserve/OpenSearch |
| 30 | `explorer` | Explorer | DATA | ✅ Exists | `tables.py` | Data explorer/browser |
| 31 | `templates` | Templates | DATA | ✅ Exists | `template_registry.py` | Template management |
| 32 | `settings` | Claude | SETTINGS | ✅ Exists | `settings.py` | Claude provider settings |
| 33 | `settings-cybersecsuite` | CyberSecSuite | SETTINGS | ✅ Exists | `settings.py` | Suite-wide settings |

---

## Backend Dashboard API Handlers

### Source: `src/dashboard/api/*.py`

**Total Documented Handlers: 32** (as of latest audit)

| # | Module | Handler | Frontend Item | Status | Purpose |
|---|--------|---------|-------------|--------|---------|
| 1 | `accounts.py` | Account mgmt | — | ⚠️ Orphan | User account management |
| 2 | `a2a_crud.py` | A2A CRUD | `a2a` | ✅ Mapped | Agent-to-Agent protocol |
| 3 | `agent_crud.py` | Agent CRUD | `agent-factory`, `agent-query` | ✅ Mapped | Agent creation/query |
| 4 | `agent_stream.py` | Agent streaming | — | ⚠️ Orphan | Stream agent responses |
| 5 | `agents.py` | Agent mgmt | `agent-crafter` | ✅ Mapped | Agent behavior management |
| 6 | `bootstrap.py` | Bootstrap API | — | ⚠️ Orphan | Initial setup/config |
| 7 | `charts.py` | Chart data | — | ⚠️ Orphan | Chart/dashboard metrics |
| 8 | `core.py` | Core handlers | `health`, `usage`, `telemetry`, `providers-hub` | ✅ Mapped | System health, usage, providers |
| 9 | `dbus.py` | D-Bus integration | — | ⚠️ Orphan | System D-Bus calls |
| 10 | `flowgraph.py` | Flowgraph | `flowgraph` | ✅ Mapped | Workflow visualization DAG |
| 11 | `forensic.py` | Forensics suite | `investigations`, `findings`, `iocs`, `yara`, `audit` | ✅ Mapped | Forensic investigation features |
| 12 | `intel_sources.py` | Intel feeds | `intel` | ✅ Mapped | Threat intelligence sources |
| 13 | `marketplace.py` | Marketplace | `marketplace`, `marketplace-factory` | ✅ Mapped | Agent marketplace |
| 14 | `memory_chat.py` | Memory chat | `chat` | ✅ Mapped | Conversational memory |
| 15 | `openobserve_stats.py` | OpenObserve stats | `opensearch` | ✅ Mapped | Observability metrics |
| 16 | `ops.py` | Operations | `cases`, `tasks`, `pocs` | ✅ Mapped | Investigation operations |
| 17 | `page.py` | Page builder | — | ⚠️ Orphan | Dynamic page generation |
| 18 | `plugin.py` | Plugin system | — | ⚠️ Orphan | Browser plugin integration |
| 19 | `projects.py` | Projects mgmt | — | ⚠️ Orphan | Project management |
| 20 | `prompts_crud.py` | Prompts CRUD | `prompts` | ✅ Mapped | Prompt management |
| 21 | `proxy_memory_chat.py` | Proxy chat | `routing` | ✅ Mapped | AI proxy routing |
| 22 | `qol_agent_presets.py` | QoL presets | — | ⚠️ Orphan | Quality-of-life presets |
| 23 | `qol_endpoints.py` | QoL endpoints | `qol-controls` | ✅ Mapped | QoL control endpoints |
| 24 | `qol.py` | QoL settings | `qol-controls` | ✅ Mapped | QoL configuration |
| 25 | `sdk_options.py` | SDK options | `sdk-lab` | ✅ Mapped | SDK configuration |
| 26 | `sdk_session.py` | SDK sessions | `sdk-lab` | ✅ Mapped | SDK session management |
| 27 | `sdk_tool.py` | SDK tools | — | ⚠️ Orphan | SDK tool registry |
| 28 | `settings.py` | Settings | `settings`, `settings-cybersecsuite` | ✅ Mapped | System settings |
| 29 | `settings_toggles.py` | Settings toggles | — | ⚠️ Orphan | Feature toggles |
| 30 | `sse.py` | Server-sent events | — | ⚠️ Orphan | Real-time event streaming |
| 31 | `startup.py` | Startup routines | — | ⚠️ Orphan | System startup/init |
| 32 | `tables.py` | Table data | `explorer` | ✅ Mapped | Data explorer tables |
| 33 | `team_builder.py` | Team builder | `team-builder` | ✅ Mapped | Multi-agent teams |
| 34 | `template_registry.py` | Templates | `templates` | ✅ Mapped | Template registry |
| 35 | `ts_proxy.py` | TypeScript proxy | — | ⚠️ Orphan | Frontend proxy integration |
| 36 | `vault_status.py` | Vault status | — | ⚠️ Orphan | Vault status API |
| 37 | `workflows.py` | Workflows | `workflows` | ✅ Mapped | Workflow orchestration |

**Total Backend Handlers: 37** (including orphans)

---

## Mapping Analysis

### Summary

| Category | Count | Details |
|----------|-------|---------|
| **Mapped (Frontend ↔ Backend)** | 29 | Sidebar item has corresponding backend handler |
| **Frontend Only (No Backend)** | 1 | `compliance` — sidebar item exists but no handler |
| **Backend Only (No Frontend)** | 8 | Orphan handlers with no sidebar item |
| **Ambiguous/Multi-Mapped** | 0 | No conflicts or overlaps |
| **Total Frontend Items** | 33 | — |
| **Total Backend Handlers** | 37 | — |

### Frontend-Only Items (Missing Backend)

| ID | Label | Group | Status | Recommendation |
|----|-------|-------|--------|--|
| `compliance` | Compliance | FORENSICS | ❌ Orphan | **Action Required (T###):** Create `compliance.py` handler in `src/dashboard/api/` or remove sidebar item |

### Backend-Only Items (Missing Frontend)

| Module | Purpose | Status | Recommendation |
|--------|---------|--------|--|
| `accounts.py` | Account mgmt | ⚠️ Orphan | Determine if sidebar item needed; if yes, create `accounts` nav item |
| `agent_stream.py` | Stream responses | ⚠️ Orphan | Internal utility; no sidebar needed |
| `bootstrap.py` | Setup/config | ⚠️ Orphan | Internal utility; triggered on startup, no sidebar needed |
| `charts.py` | Chart metrics | ⚠️ Orphan | Used by other panels; no dedicated sidebar item needed |
| `dbus.py` | D-Bus integration | ⚠️ Orphan | Linux-only system integration; no sidebar needed |
| `page.py` | Page builder | ⚠️ Orphan | Dynamic page gen; may need frontend dashboard item (T###) |
| `plugin.py` | Plugin system | ⚠️ Orphan | Browser plugin integration; consider frontend item |
| `projects.py` | Projects mgmt | ⚠️ Orphan | Project organization; consider sidebar item (T###) |
| `qol_agent_presets.py` | QoL presets | ⚠️ Orphan | Internal presets; no dedicated item needed |
| `sdk_tool.py` | SDK tools | ⚠️ Orphan | Internal SDK registry; no sidebar needed |
| `settings_toggles.py` | Feature toggles | ⚠️ Orphan | May be part of `settings` panel; verify mapping |
| `sse.py` | Real-time events | ⚠️ Orphan | Internal utility; no sidebar needed |
| `startup.py` | Startup routines | ⚠️ Orphan | Internal utility; no sidebar needed |
| `ts_proxy.py` | TypeScript proxy | ⚠️ Orphan | Frontend proxy; internal only, no sidebar needed |
| `vault_status.py` | Vault status | ⚠️ Orphan | Vault integration; may need sidebar item (T###) |

---

## Mapping Table (Detailed)

### PLATFORM Group (5 items)

| Frontend | Backend | Routes | Status |
|----------|---------|--------|--------|
| `health` | `core.py` | `/api/health`, `/api/crypto` | ✅ Mapped |
| `usage` | `core.py` | `/api/usage` | ✅ Mapped |
| `telemetry` | `core.py` + OpenTelemetry | `/api/overview`, `/api/telemetry/*` | ✅ Mapped |
| `providers-hub` | `core.py` | `/api/providers`, `/api/providers-hub` | ✅ Mapped |
| — | `settings_toggles.py` | `/api/settings/toggles` | ⚠️ May belong to settings |

### AI PROXY Group (2 items)

| Frontend | Backend | Routes | Status |
|----------|---------|--------|--------|
| `routing` | `proxy_memory_chat.py` | `/api/proxy/*` | ✅ Mapped |
| `qol-controls` | `qol.py` + `qol_endpoints.py` | `/api/qol/*` | ✅ Mapped |

### AGENTS Group (10 items)

| Frontend | Backend | Routes | Status |
|----------|---------|--------|--------|
| `chat` | `memory_chat.py` | `/api/chat/*`, `/api/memory/*` | ✅ Mapped |
| `agent-factory` | `agent_crud.py` | `/api/agents/create`, `/api/agents/list` | ✅ Mapped |
| `agent-crafter` | `agents.py` | `/api/agents/config`, `/api/agents/update` | ✅ Mapped |
| `team-builder` | `team_builder.py` | `/api/team/*`, `/api/teams/*` | ✅ Mapped |
| `agent-query` | `agent_crud.py` | `/api/agents/query`, `/api/agents/get/*` | ✅ Mapped |
| `workflows` | `workflows.py` | `/api/workflows/*` | ✅ Mapped |
| `flowgraph` | `flowgraph.py` | `/api/flowgraph/*` | ✅ Mapped |
| `prompts` | `prompts_crud.py` | `/api/prompts/*` | ✅ Mapped |
| `sdk-lab` | `sdk_options.py` + `sdk_session.py` | `/api/sdk/*` | ✅ Mapped |
| `marketplace` + `marketplace-factory` | `marketplace.py` | `/api/marketplace/*` | ✅ Mapped |

### OPERATIONS Group (4 items)

| Frontend | Backend | Routes | Status |
|----------|---------|--------|--------|
| `cases` | `ops.py` | `/api/ops/cases/*` | ✅ Mapped |
| `tasks` | `ops.py` | `/api/ops/tasks/*` | ✅ Mapped |
| `pocs` | `ops.py` | `/api/ops/pocs/*` | ✅ Mapped |
| `a2a` | `a2a_crud.py` | `/api/a2a/*` | ✅ Mapped |

### FORENSICS Group (6 items)

| Frontend | Backend | Routes | Status |
|----------|---------|--------|--------|
| `investigations` | `forensic.py` | `/api/forensic/investigations/*` | ✅ Mapped |
| `findings` | `forensic.py` | `/api/forensic/findings/*` | ✅ Mapped |
| `iocs` | `forensic.py` | `/api/forensic/iocs/*` | ✅ Mapped |
| `yara` | `forensic.py` | `/api/forensic/yara/*` | ✅ Mapped |
| `intel` | `intel_sources.py` | `/api/intel/*` | ✅ Mapped |
| `audit` | `forensic.py` | `/api/forensic/audit/*` | ✅ Mapped |
| `compliance` | ❌ **MISSING** | — | ❌ **NO HANDLER** |

### DATA Group (3 items)

| Frontend | Backend | Routes | Status |
|----------|---------|--------|--------|
| `opensearch` | `openobserve_stats.py` | `/api/openobserve/*`, `/api/opensearch/*` | ✅ Mapped |
| `explorer` | `tables.py` | `/api/tables/*`, `/api/explorer/*` | ✅ Mapped |
| `templates` | `template_registry.py` | `/api/templates/*` | ✅ Mapped |

### SETTINGS Group (2 items)

| Frontend | Backend | Routes | Status |
|----------|---------|--------|--------|
| `settings` | `settings.py` | `/api/settings/*` | ✅ Mapped |
| `settings-cybersecsuite` | `settings.py` | `/api/settings/cybersecsuite/*` | ✅ Mapped |

---

## Action Items

### Phase 1 Documentation (Current)

- [x] Create this inventory document
- [x] Identify unmapped items
- [x] Document discrepancies

### Phase 2 Backend (T###)

- [ ] **T###** — Create `compliance.py` handler (missing backend for `compliance` sidebar)
- [ ] **T###** — Create `accounts` sidebar item (orphan `accounts.py` handler)
- [ ] **T###** — Verify `settings_toggles.py` mapping (may be internal)
- [ ] **T###** — Decide: keep or remove `page.py`, `plugin.py`, `projects.py`, `vault_status.py` backend utilities

### Phase 2 Frontend (T###)

- [ ] **T###** — Add `compliance` backend integration (create handler first)
- [ ] **T###** — Consider `accounts` nav item (if needed)
- [ ] **T###** — Review orphan backends; add sidebar items if warranted
- [ ] **T###** — Update `nav.ts` with new items and verify all map correctly

### Quality Assurance (Ongoing)

- [ ] **Every PR:** Verify new sidebar items have backend handlers
- [ ] **Every PR:** Verify new backend handlers have frontend items (or documented as internal)
- [ ] **Quarterly:** Run this audit to catch drift

---

## File References

### Frontend Navigation
- **File:** `src/frontend/src/constants/nav.ts`
- **Type:** TypeScript constants
- **Structure:** `NAV_ITEMS: NavItem[]` array

### Backend Handlers
- **Directory:** `src/dashboard/api/`
- **Pattern:** Each `.py` file is a module with FastAPI route handlers
- **Routes:** Defined via `/api/**` endpoints

### Documentation
- **This document:** `docs/SIDEBAR-PANEL-MAP.md`
- **Related:** `docs/AGENT-DELEGATION.md`, `plans/plan.md`

---

## Summary

✅ **29/33 sidebar items have mapped backend handlers (88%)**

❌ **1 sidebar item missing backend:** `compliance`

⚠️ **8 backend handlers without sidebar items:** Mostly internal utilities, some may warrant frontend items

**Next Step:** Create missing `compliance.py` handler to achieve 100% frontend↔backend mapping.
