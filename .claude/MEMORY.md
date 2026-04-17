# CyberSecSuite — MEMORY.md

---

## CRITICAL ARCHITECTURE — READ FIRST

### Claude → ASGI Proxy → Provider routing

Claude Code (and `agent_sdk.py`) routes ALL Claude API calls through the local ASGI proxy.

```
Claude Code / claude-agent-sdk query()
        │  ANTHROPIC_BASE_URL=http://localhost:8000/v1
        ▼
  ASGI /v1/* (AI Proxy, OpenAI-compat)
        │  AI Proxy routing (combo.py, 13 strategies)
        ├── Anthropic (default)
        ├── OpenAI / Gemini / Groq / Mistral / DeepSeek / XAI / Together / OpenRouter
        └── default_strategy: "cost-optimized"
```

**`agent_sdk.py` — must set base_url in `ClaudeAgentOptions`:**
```python
opts = ClaudeAgentOptions(
    allowed_tools=allowed,
    agents=agents,
    base_url=os.environ.get("ANTHROPIC_BASE_URL", "http://localhost:8000/v1"),
    api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
)
```

### ASGI Mount Map (`src/proxy/asgi.py`)
| Path                      | What                                                       |
|---------------------------|------------------------------------------------------------|
| `/health`                 | DB health check (200/503)                                  |
| `/dashboard/*`            | Dashboard UI + 25 REST + 4 SSE endpoints (30 routes total) |
| `/v1/*`                   | AI Proxy (OpenAI-compat) ← Claude routes here              |
| `/a2a/*`, `/.well-known/` | A2A JSON-RPC 2.0 server                                    |

### settings.json (`.claude/settings.json`) — 12 sections
```json
{
  "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" },
  "agent": "cybersec-agent",
  "version": "0.1.0",
  "asgi": { "host": "127.0.0.1", "port": 8000, "alt_port": 8080, "tls_port": 8433 },
  "mcp": { "servers": ["cybersec", "dystopian"], "tool_prefix": "mcp__" },
  "proxy": { "enabled": true, "default_strategy": "cost-optimized" },
  "crypto": { "algorithm": "Ed25519", "hash": "blake2b", "hash_digest_size": 32 },
  "signing": { "algorithm": "Ed25519", "token_format": "frontmatter.payload", "default_expiry_hours": 8760 },
  "artifacts": { "checksum_algorithm": "blake2b", "signature_log_enabled": true },
  "keys": { "directory": "/etc/dystopian-crypto/keys" },
  "cache": { "integrity_key": "cache_integrity", "default_ttl_hours": 24 },
  "security": { "min_password_length": 16, "audit_logging": true }
}
```

`"agent": "cybersec-agent"` → Claude Code auto-loads `.claude/agents/cybersec-agent.md` as orchestrator.

### Ports
| Port | What                | Status                        |
|------|---------------------|-------------------------------|
| 8000 | ASGI HTTP (primary) | ✅                             |
| 8080 | ASGI HTTP (alt)     | ⚠️ exposed, no alt listener   |
| 8433 | ASGI HTTPS          | ⚠️ SSL helper ready, no certs |
| 5432 | PostgreSQL          | ✅ localhost                   |

---

## Codebase Map

### Root
| File                 | Lines | Purpose                                                                 |
|----------------------|-------|-------------------------------------------------------------------------|
| `mcp_server.py`      | 1288  | FastMCP stdio — 29 tools (→ being replaced by src/mcp/cybersec/) |
| `mcp.json`           | 86    | 5 MCP servers for Claude Code CLI                                       |
| `pyproject.toml`     | —     | Python 3.14, uv, all deps                                               |
| `Makefile`           | —     | `make serve`, `make test`, etc.                                         |
| `docker-compose.yml` | —     | ASGI + PostgreSQL + Redis, YAML anchors `&common`/`&db-env`/`&ai-keys`  |
| `PROPOSAL.md`        | ~240  | Plugin separation architecture proposal                                 |
| `PROPOSAL_MEM.md`    | ~250  | Global uncompressed claude memory cache proposal                        |

### src/
| File                  | Lines | Purpose                                                                 |
|-----------------------|-------|-------------------------------------------------------------------------|
| `src/proxy/asgi.py`   | 123   | ASGI app, env-driven ports, mounts all sub-apps, TelemetryMiddleware    |
| `src/manage.py`       | ~450  | CLI management (`manage.py serve`, `case-open`, `ssl`, `vault`, `check`, etc.) |
| `src/logger.py`       | 30    | Structured logger                                                       |
| `src/mcp/__init__.py` | ~30   | `all_servers()` → `{cybersec, dystopian}`, `allowed_tools()` → 34 tools |

### src/a2a/
| File                | Lines | Purpose                                                              |
|---------------------|-------|----------------------------------------------------------------------|
| `agent_sdk.py`      | 358   | SDK bridge — model mapping, PreToolUse audit hook, run_agent_query() |
| `agent_loader.py`   | 272   | Loads `.claude/agents/*.md` → AgentCards                             |
| `orchestrator.py`   | 365   | A2A task orchestration                                               |
| `dev_agents.py`     | 322   | Dev agent stubs (SDK-wired ✅)                                        |
| `cybersec_agent.py` | 350   | CybersecAgent (SDK-wired ✅)                                          |
| `server.py`         | 236   | A2A JSON-RPC server                                                  |
| `client.py`         | 205   | A2A client                                                           |
| `registry.py`       | 257   | AgentRegistry — remote A2A discovery                                 |
| `task_store.py`     | 157   | In-memory + DB task store                                            |
| `models.py`         | 215   | A2A Pydantic models                                                  |
| `enums.py`          | —     | A2A enums                                                            |
| `agent.py`          | —     | BaseA2AAgent                                                         |

### src/ai_proxy/
| File                        | Lines | Purpose                                                   |
|-----------------------------|-------|-----------------------------------------------------------|
| `routes.py`                 | 224   | OpenAI-compat `/v1/*` endpoints                           |
| `providers/registry.py`     | 1040  | **51 providers**, model lists, cost metadata, auth types  |
| `routing/combo.py`          | 574   | 13-strategy routing engine, circuit breaker, budget guard |
| `translators/core.py`       | 275   | Request/response translation between formats              |
| `services/rate_limiter.py`  | 159   | Rate limiting per provider                                |
| `services/usage_tracker.py` | 139   | Token usage tracking                                      |
| `executors/base.py`         | 256   | Base executor for async provider calls                    |
| `executors/playwright.py`   | 270   | Playwright-based browser AI provider                      |
| `cli.py`                    | 273   | CLI for provider management, usage, cost reports          |

### src/crypto/ (10 files ✅)
Ed25519 signing, BLAKE2b-256, Argon2id (mem=262144, iters=4), AES-256-GCM.
Keys: `/etc/dystopian-crypto/keys`. Vault: `~/.dystopian-crypto/vault/`.
| File | Lines | Purpose |
|------|-------|---------|
| `pydantic_models.py` | 494 | Pydantic validation models |
| `artifact_manager.py` | 376 | Artifact signing/verification |
| `key_manager.py` | 362 | KeyManager + PasswordManager |
| `ssl_signer.py` | 277 | SSLArtifactSigner (Ed25519) |
| `vault.py` | ~120 | **NEW** File-based encrypted secret vault |
| `cli_integration.py` | ~350 | **REWRITTEN** Runnable Click CLI: ssl + vault commands |
| `template_renderer.py` | 228 | Certificate template renderer |
| `cache.py` | 270 | Crypto cache layer |
| `config.py` | 253 | Crypto configuration |

### src/db/ (44 model files, 70 model classes ✅)
PostgreSQL via Tortoise ORM (asyncpg). DB: `cybersec_forensics`.
Key models: Investigation, Finding, IOC, YaraRule, NetworkEvent, ComplianceRecord, AuditLog, ApiUsageLog, A2ATask, Artifact, MitreTechnique, CVE, CAPEC, CWE, ThreatProfile, and 25+ more.
**Fixtures**: 6 JSON files in `src/db/fixtures/` (mitre_techniques, mitre_actors, mitre_software, cwe_entries, capec_entries, **cve_entries**)
**Known fix**: Duplicate AuditLog (audit.py→re-export from core.py), duplicate SharedEntry removed from investigation.py, empty intelligence.py removed from MODEL_MODULES.
Shell scripts: `init_db.sh`, `init_session.sh`, `backup_db.sh`.

### src/checks/ (NEW ✅)
Integrity check module — validates model FK consistency, fixture coverage, and config file paths.
| File | Purpose |
|------|---------|
| `integrity.py` | `check_models()`, `check_fixtures()`, `check_config()`, `run_all_checks()` |
| `__init__.py` | Re-exports |

**Results**: 0 model errors (after fix), 3 config errors (missing MCP dirs, stale entry point), 18 warnings (missing fixtures).

### src/telemetry/ (5 files ✅ new)
In-process metrics store with ring-buffer, percentile summaries, ASGI middleware.
| File | Purpose |
|------|---------|
| `store.py` | `MetricsStore` (asyncio.Lock, deque maxlen=1000), `TelemetryEvent`, `MetricSummary` (p50/p95/p99/mean/count/rps) |
| `middleware.py` | `TelemetryMiddleware` — ASGI, path normalisation (`/{id}`, `/{uuid}`), skips /health+/static |
| `decorators.py` | `@timed(name)`, `@counted(name)` async decorators |
| `collector.py` | `TelemetryCollector` — 15s poll, 100-snapshot ring history, `get_history(metric, n)` for sparklines |
| `__init__.py` | Module singleton `metrics_store`, `collector`, `record_event()`, `get_snapshot()` |

Mounted in `src/proxy/asgi.py`: `app.add_middleware(TelemetryMiddleware)`. Collector started in `_on_startup()`, stopped in `_on_shutdown()`.

### src/dashboard/routes.py (1620L)
27 REST endpoints + 4 SSE endpoints + 1 HTML root = 32 routes. All HTML inline in `_DASHBOARD_HTML` string.
REST: overview, providers, usage, health, crypto, a2a, investigations, db-counts, agents, routing, agent-factory, prompts, cases, tasks, tasks/create, tasks/{id}, tasks/{id}/cancel, findings, iocs, yara, network, intelligence, audit, compliance, **nist-csf**, **nist-ai-rmf**, telemetry
SSE: /sse/cases, /sse/tasks, /sse/health, /sse/telemetry
Current tabs: Cases, Sessions, Agents, Providers, Strategies, Tools, Tasks, Findings, IOCs, Network, Intel, Compliance, Audit.

### .claude/ system
| Component    | Files                                                      | Status                       |
|--------------|------------------------------------------------------------|------------------------------|
| `agents/`    | 33 agents + AGENT_FACTORY + 3 teams (in `teams/` subdir)   | ✅ all consistent frontmatter |
| `hooks/`     | 28 .py files (18 event handlers + 10 modules) + hooks.json | ⚠️ NEVER AUDITED             |
| `commands/`  | 7 slash commands + config.py + `__init__.py` + README.md   | ⚠️ NEVER AUDITED             |
| `skills/`    | **933 SKILL.md** across 28 active domains                 | ✅ RESTRUCTURED               |
| `templates/` | 14 template files across 6 subdirs                         | Not reviewed                 |

#### templates/ structure
```
templates/
  artifact.md
  baselines/    kernel.md, network.md, persistence.md, processes.md
  iocs/         cleared.md, ioc-db.md, watchlist.md
  project/      findings.md
  reports/      investigation-report.md
  session/      session-manifest.json, timeline.md
  threat-intelligence/  session-index.md, threat-profile.md
```

#### hooks/ — 28 .py files
**18 event handlers** (registered in hooks.json):
`agent_end`, `agent_start`, `baseline_updated`, `evidence_collected`, `finding_confirmed`,
`first_init`, `investigation_end`, `investigation_start`, `ioc_discovered`, `mode_switch`,
`permission_violation`, `phase_end`, `phase_start`, `post_tool_use`, `pre_tool_call`,
`root_command_executed`, `session_end`, `session_start`

**10 additional modules** (not in hooks.json):
`_utils`, `utils` (shared utilities), `database`, `exact_match_cache`, `uvloop_integration`,
`yara_rule_generator`, `yara_rule_optimizer`, `yara_rule_tester`, `termmate_idle`, `threat_detected`

#### commands/ — 7 slash commands
| Command        | Purpose                                       |
|----------------|-----------------------------------------------|
| `hunt`         | Check for suspicious processes and injections |
| `browser-hunt` | Browser artifact forensics                    |
| `memory-dump`  | Process injection indicators                  |
| `net-hunt`     | ARP spoofing detection                        |
| `mode-switch`  | Switch blue/red/purple mode                   |
| `setup`        | Run manage.py commands                        |
| `test-config`  | Test configuration validation                 |

Supporting files: `config.py`, `__init__.py`, `README.md`

#### hooks/_utils.py — shared utilities
`ensure_structure`, `get_project_dir`, `get_session_dir`, `audit`, `emit`, `hook_context`

---

## Agent System

### `"agent": "cybersec-agent"` — Default Claude Code Agent
Loads `.claude/agents/cybersec-agent.md`. Orchestrator with `role: orchestrator`.
Accepts `blue|red|purple` mode. Delegates to all 32 specialist sub-agents.

### All 32 agents — frontmatter consistent ✅
Model tiers:
- **Haiku** — watchdog, command-verifier
- **Sonnet** — 27 agents: all analysts, developers, layer2-7 specialists (default)
- **Opus** — firmware-analyst, reverse-engineer, AGENT_FACTORY

### Two Execution Paths (NEVER conflate)
**A. Agent SDK** (internal): `query()` → `http://localhost:8000/v1` → provider routing → MCP tools + subagents
**B. A2A Protocol** (external): `POST /a2a` JSON-RPC → OrchestratorAgent → registry → `execute()`

### mcp.json — 5 MCP servers for Claude Code CLI
| Key                      | Server                                                         |
|--------------------------|----------------------------------------------------------------|
| `cybersec`               | Main forensics (29 tools, stdio, `mcp_server.py`)              |
| `dystopian-crypto`       | Crypto/CA/GPG (`mcps/dystopian-crypto-mcp/app.py` — **EMPTY**) |
| `kerneldev`              | Kernel module dev (`kerneldev_mcp.server`)                     |
| `token-optimization-mcp` | Token caching                                                  |
| `playwright-stealth-mcp` | Browser automation                                             |

---

## Skills System

### Philosophy
**Skills = components** (tools, protocols, systems, software).
**Actions = leaf directory names** (the specific tool/technique applied to a component).
**Activities ≠ domains** — `red-team/`, `forensics/`, `incident-response/` are methods, not components.

### Current State (933 skills, 26 active domains)
| Type                     | Count   | Description                                              |
|--------------------------|---------|----------------------------------------------------------|
| Project-native (full)    | 170+    | Rich SKILL.md with deep taxonomy, MITRE/CWE/CVE headers  |
| Anthropic-integrated     | 752     | Full Anthropic workflow + CyberSecSuite integration      |
| **Total**                | **933** | All in `.claude/skills/`, indexed in `INDEX.md`          |

**Frontmatter** — ✅ COMPLETE
- Removed: `mcpServers`, `version`, `license`, `author` (redundant/global)
- Action collision resolution: multi-level path names (e.g., `analysis-volatility`, `persistence-malware`)

### Domain Structure (after Phase 5+7 restructuring ✅)
```
.claude/skills/               ← root (933 SKILL.md, 26 active domains)
├── forensics/         (150)  # disk, memory, network, log, email, mobile, cloud, usb
│                             #   + hunting, ioc, analysis, intelligence, mitre (from threat-intel)
├── cloud-security/    (116)  # aws, azure, gcp, containers, kubernetes, devsecops
├── web-application/    (97)  # injection, xss, ssrf, api, pentest, owasp
├── malware/            (74)  # static, dynamic, reversing, persistence, c2, yara, triage
├── network/            (67)  # firewall, ids, wireless, vpn, dns, lateral, recon
├── identity/           (53)  # ad, kerberos, oauth, saml, pam, mfa, okta
├── incident-response/  (39)  # triage, containment, playbooks, phishing, cloud, insider
├── vulnerabilities/    (32)  # scanning, sca, prioritization, remediation, exploit
├── processes/          (30)  # linux/{proc-fs,ptrace,namespace,cgroup,ld-preload,daemon,socket}/
│                             #   windows/{handle,thread,process,dll,token,wmi}/
├── filesystem/         (28)  # ext4, ntfs, fat32, xfs, btrfs, tmpfs, procfs, vfs
├── siem-soc/           (27)  # splunk, elastic, detection, correlation, tuning
├── industrial/         (25)  # scada, plc, modbus, dnp3, iot (dissolved from ot-ics)
├── database/           (24)  # mysql, postgres, sqlite, mssql, redis, mongodb, elasticsearch
├── endpoint-security/  (23)  # edr, av, policy, dlp, hardening
├── browser/            (22)  # chrome, firefox, brave, chromium, extension, forensics
├── crypto-pki/         (20)  # tls, certificates, pki, key-management, hashing
├── network-filesystem/ (18)  # smb, nfs, cifs, webdav, ftp, rsync, iscsi, samba
├── ops/                (17)  # mode, scope, engagement, purpleteam, socialeng, physical
├── steganography/      (15)  # image, audio, video, document, tool, network
├── intel-platform/     (13)  # platforms, feeds (from threat-intel)
├── compliance/         (13)  # cis, nist, gdpr, hipaa, pci, sox, iso
├── osint/               (9)  # shodan, darkweb, social (from threat-intel)
├── mobile/              (8)  # android, ios, apk analysis
├── kernel-os/           (8)  # linux, firmware, lkm, ebpf
├── deception/           (5)  # honeypots, canaries
└── hardening/           (0)  # index-only, links to */hardening/ skills
```

### Naming Rules
- **Taxonomy dirs**: CAN have hyphens (`cloud-security`, `crypto-pki`, `red-team`)
- **Leaf skill dirs**: Single-word only (`volatility3`, `cobaltstrike`, `kerberoasting`)
- **Deep taxonomy** (new classical domains): `name:` = join layers 2→last with hyphens; last dir = action verb
  - Example: `network/protocol/tcp/syn-flood/detect` → `name: protocol-tcp-syn-flood-detect`
- 224 explicit collision overrides for disambiguation

### SKILL.md Format
```yaml
---
name: skill-name
description: "..."
action: leaf-dir-name
domain: cybersecurity             # Anthropic-sourced only
subdomain: malware-analysis       # Anthropic-sourced only
tags: [volatility, memory]
d3fend_techniques: [...]          # Anthropic-sourced only (139 skills)
nist_csf: [DE.AE-02]             # Anthropic-sourced only (all 754)
mitre_attack: [T1055, T1003]     # 644 skills
cwe: [CWE-120]                   # 99 skills
cve: [CVE-2021-44228]            # 51 skills
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
source: Anthropic-Cybersecurity-Skills   # absent for 26 project-native
---
```

**Field inventory** (all 780 skills):
| Field | Present | Notes |
|-------|---------|-------|
| `name`, `description`, `action` | 780 | always present |
| `model`, `maxTurns`, `tools` | 780 | always present |
| `tags` | 780 | 2,283 unique |
| `mitre_attack` | 644 | 131 unique technique IDs |
| `nist_csf` | 752 | 46 unique subcategories (all Anthropic) |
| `d3fend_techniques` | 139 | D3FEND defensive techniques |
| `domain`, `subdomain` | 752 | Anthropic-sourced only |
| `source` | 752 | `Anthropic-Cybersecurity-Skills` |
| `cwe` | 99 | 33 unique CWE IDs |
| `cve` | 51 | 58 unique CVE IDs |
| `skills` | 22 | project-native cross-refs |

### Anthropic Skills Source
All 752 from `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/`
Full content copied with adapted frontmatter. Extra content (LICENSE, scripts/, references/, assets/) NOT YET COPIED.

### Key Files
- `INDEX.md` — master sorted list (auto-generated, 778 entries, 47KB)
- `DEV_REFERENCE.md` — developer reference (724 lines)
- `ops/mode/blue-team/SKILL.md` — blue team mode activation
- `red-team/SKILL.md` — red team orchestrator index
- `kernel-os/linux/lkm/kerneldev-forensic/` — full skill with config/, examples/, scripts/, templates/

---

## mcp_server.py Split Plan

Split `mcp_server.py` (1288L, 29 tools) into `src/mcp/cybersec/` subpackage:

```
src/mcp/
  __init__.py              # all_servers() → dict, allowed_tools() → list[str]
  cybersec/
    __init__.py            # create_sdk_mcp_server("cybersec", tools=[ALL 29 tools])
    helpers.py             # ScopeState, scope vars, helper funcs (lines 16-142)
    findings.py            # add_finding, add_ioc, query_findings, update_risk_register (4)
    db.py                  # db_healthcheck, bootstrap_intelligence (2)
    intelligence.py        # suggest_mitre, get_project_memory (2)
    layers.py              # share_to_layers, get_layer_value (2)
    cache.py               # cache_lookup, cache_store, cache_analytics, cache_invalidate (4)
    proxy.py               # 10 proxy tools
    session.py             # session_snapshot, agent_registry, best_provider (3)
    cases.py               # case_open, case_status (2)
  dystopian.py             # 5 crypto tools wrapping src/crypto/
```

`mcp_server.py` → thin FastMCP stdio shim after split.
Tool naming: `mcp__cybersec__<tool>` (SDK) / `cybersec.<tool>` (FastMCP stdio).

---

## OmniRoute Integration

### OmniRoute MCP Server — 16+ Tools
**Location**: `/home/daen/Projects/OmniRoute/open-sse/mcp-server/`
**Status**: PENDING (todo: `omniroute-integrate`)

#### Essential Tools (8)
| Tool                            | Purpose                                  |
|---------------------------------|------------------------------------------|
| `omniroute_get_health`          | Gateway health, circuit breakers, uptime |
| `omniroute_list_combos`         | All configured combos with models        |
| `omniroute_get_combo_metrics`   | Performance metrics for a specific combo |
| `omniroute_switch_combo`        | Switch active combo by ID/name           |
| `omniroute_check_quota`         | Quota status per provider or all         |
| `omniroute_route_request`       | Send a chat completion through OmniRoute |
| `omniroute_cost_report`         | Cost analytics for a time period         |
| `omniroute_list_models_catalog` | Full model catalog with capabilities     |

#### Advanced Tools (8)
| Tool                               | Purpose                                 |
|------------------------------------|-----------------------------------------|
| `omniroute_simulate_route`         | Dry-run routing simulation              |
| `omniroute_set_budget_guard`       | Session budget with degrade/block/alert |
| `omniroute_set_routing_strategy`   | Runtime strategy switch                 |
| `omniroute_set_resilience_profile` | Apply resilience presets                |
| `omniroute_test_combo`             | Live-test all models in a combo         |
| `omniroute_get_provider_metrics`   | Detailed per-provider metrics           |
| `omniroute_best_combo_for_task`    | Task-fitness recommendation             |
| `omniroute_explain_route`          | Explain a past routing decision         |

#### Skill Tools (3)
`omniroute_skills_list`, `omniroute_skills_enable`, `omniroute_skills_execute`

#### Integration
- Register as external MCP in `mcp.json`
- Env: `OMNIROUTE_API_KEY`, `OMNIROUTE_BASE_URL=http://localhost:8888`
- Allowed tools: `mcp__omniroute__*`

---

## Roadmap

### ✅ Done
- Phase 0 — agent frontmatter, ports, docker, settings, deleted dead middleware
- Docs — 8 docs written (docs/architecture, api, agents, configuration, contributing, deployment, mcp-tools, quickstart)
- Skills taxonomy — 778 → **933** SKILL.md across 24+ domains (web-security→web-application, ot-ics dissolved, 6 classical domains expanded with 189 new deep-hierarchy skills)
- MCP package split — `src/mcp/` package: `cybersec/` (29 tools) + `dystopian.py` (5 tools) + SDK compat shim → 34 tools, `all_servers()` + `allowed_tools()` — commit f0e8b72
- New agents — `token-optimizer.md` (haiku, redundancy detection + prompt compression + cache seeds) — 33 agents total
- Phase A2 — A2A stubs wired to SDK (model mapping, PreToolUse audit hook, real AI execution) — commits 3cfa5a0
- Phase D (partial) — Telemetry stack complete (MetricsStore, middleware, decorators, collector, TelemetryMiddleware mounted) — commits 44bcdd7, 1a688c6, 3936eaf
- Dashboard expansion — 30 routes total (was 16+3); 7 data endpoints + telemetry + task CRUD — commits 13af280, 3936eaf
- NIST fixtures downloaded — `data/fixtures/nist_csf_2.json` (185 subcategories) + `data/fixtures/nist_ai_rmf.json` (72 subcategories)
- NIST DB models + seeds + CLI + dashboard endpoints — `NistCsfControl`, `NistAiRmfControl`, `seed_nist_csf()`, `seed_nist_ai_rmf()`, `seed-nist-csf/ai-rmf/all` CLI commands, `/api/nist-csf` + `/api/nist-ai-rmf` endpoints (commit 72de387)
- Skills: web-security renamed → web-application; ot-ics dissolved → 3-6 level hierarchy (ics/, iot/, sector/) (commit 3db39fd)
- **MCP pkg split** — `src/mcp/cybersec/` (8 submodules, 29 tools) + `src/mcp/dystopian.py` (5 crypto tools) + `_sdk_compat.py` shim → commit f0e8b72
- **Classical domains expanded** — 189 new SKILL.md: network, network-filesystem, filesystem, database, browser, processes → commit 63b4880
- **token-optimizer agent** — `.claude/agents/token-optimizer.md` (haiku, redundancy/compression specialist)

### docs/ — 8 files
`architecture.md`, `api.md`, `agents.md`, `configuration.md`, `contributing.md`, `deployment.md`, `mcp-tools.md`, `quickstart.md`

---

## Active Roadmap (Mega-Iteration)

### ✅ Phase 1 — Config, Docker, CLAUDE.md — COMPLETE (commit a3ac1d9)
- Created `CLAUDE.md` at project root (project overview, MCP tools, arch, env vars)
- Fixed `mcp.json` dystopian-crypto path (→ `src/mcp/dystopian.py`)
- Moved root `Dockerfile` → `.docker/dashboard/Dockerfile`; created `.docker/redis/Dockerfile`
- Added `cybersec-redis` service to `docker-compose.yml`

### ✅ Phase 2 — Intel DB Seeds — COMPLETE (commit 90c40be)
- Created `src/db/fixtures/`: mitre_techniques.json (30), mitre_actors.json (12), mitre_software.json (14), cwe_entries.json (18), capec_entries.json (20)
- Added `seed_mitre_techniques()`, `seed_mitre_actors()`, `seed_mitre_software()`, `seed_cwe()`, `seed_capec()` to `seeds.py`
- `initialize_default_seed_data()` now runs all 7 seeders (NIST + MITRE + CWE + CAPEC)
- `manage.py` commands: `seed`, `seed-intel`, `seed-mitre`, `seed-mitre-actors`, `seed-mitre-software`, `seed-cwe`, `seed-capec`

**Intel tables seeded**: `intel_mitre_techniques`, `intel_mitre_threat_actors`, `intel_mitre_software_families`, `intel_cwes`, `intel_capec_patterns`, `intel_cves`, `nist_csf_controls`, `nist_ai_rmf_controls`

### ✅ Phase 3 — Documentation — COMPLETE (commit 0984fda)
- Updated all 8 docs: architecture.md (2 Mermaid flowcharts), api.md, agents.md, configuration.md, contributing.md, deployment.md, mcp-tools.md, quickstart.md
- Created `docs/teams.md` — team mode, blue/red/purple responsibilities, team-task command

### ✅ Phase 4 — SKILL.md Mass Updates — COMPLETE (commit 0984fda)
- Removed `source:` field (748 files); renamed `name:` to path-based pattern (919 files)
- Added `nist_csf: []` and `capec: []` frontmatter headers to all 919 files
- **Name pattern**: `network/ids/wazuh/install/SKILL.md` → `name: ids-wazuh-install`

### ✅ Phase 5 — Domain Restructuring — COMPLETE (commit dacc0c0)
- `vulnerability/` → `vulnerabilities/` (32 skills)
- `ot-ics/` → `industrial/` (25 skills)
- `threat-intel/` dissolved (86 skills): hunting/ioc/analysis/intelligence/threat/mitre → `forensics/`; detection → `siem-soc/`; platforms/feeds → `intel-platform/` (new); osint/shodan/darkweb → `osint/` (new); brand → `ops/`
- `steganography/`: 14 new SKILL.md files (image/audio/video/document/tool/network)
- **New domains**: `intel-platform/`, `osint/`
- **Total**: 933 SKILL.md across **28 active domains**

### ✅ Phase 6 — Agent Team Task — COMPLETE
- `.claude/commands/team-task` slash command
- `manage.py team-task --team blue|red|purple --task "..." [--agents a,b]`

### ✅ Phase 7 — Vault, SSL, Fixtures, Checks, Providers — COMPLETE
- **docker-compose.yml**: YAML anchors `x-common: &common`, `x-db-env: &db-env`, `x-ai-keys: &ai-keys` — DRY config
- **Vault**: `src/crypto/vault.py` — file-based encrypted secret vault (~/.dystopian-crypto/vault/)
- **SSL CLI**: `src/crypto/cli_integration.py` rewritten — runnable Click CLI: `ssl create-ca`, `create-key`, `create-csr`, `list`, `verify`, `rotate`; vault `store`, `get`, `list`, `delete`
- **manage.py**: wired `ssl`, `vault`, `check` commands
- **CVE fixture**: `src/db/fixtures/cve_entries.json` (30 canonical CVEs), `seed_cve()`, `seed-cve` command
- **Integrity checks**: `src/checks/integrity.py` — `check_models()`, `check_fixtures()`, `check_config()`, `run_all_checks()`
- **Model fixes**: Duplicate `AuditLog` (audit.py→re-export), duplicate `SharedEntry` removed from investigation.py, empty intelligence.py removed
- **Providers**: 48 → **51** providers in `src/ai_proxy/providers/registry.py` (added kimi, qwen, chutes)
- **Flowcharts**: Updated `docs/architecture.md` — ultimate + actual Mermaid diagrams
- **Proposals**: `PROPOSAL.md` (plugin separation), `PROPOSAL_MEM.md` (Obsidian memory cache)

### Phase A — MCP Split + SDK Package ✅ COMPLETE (commit f0e8b72)
| Order | Todo                                              | Status                                       |
|-------|---------------------------------------------------|----------------------------------------------|
| 1-5   | helpers, 8 submodules, pkg, `__init__`, dystopian | ✅ all done                                   |
| 6     | `mcp-shim-update` — slim mcp_server.py            | ⚠️ pending — still 1288L with inline helpers |
| 7     | `mcp-agent-sdk-update` — wire SDK to `src/mcp/`   | pending                                      |

**Known redundancy**: `mcp_server.py` has 5 helpers duplicating `src/mcp/cybersec/helpers.py`.
FastMCP typed-param pattern prevents trivial merge — deferred to `mcp-shim-update`.

### ~~Phase A2~~ ✅ COMPLETE (commit 3cfa5a0) · ~~Phase D / D2~~ ✅ COMPLETE

### Phase B — Code Review (after A)
`review-dashboard-routes`, `review-combo-routing`, `review-mcp-server`, `review-a2a-modules`, `review-db-models`, `review-manage-cli`

### Phase C — SSL/TLS
`ssl-dystopian-integrate` → `ssl-cert-generation` → `ssl-cli-commands` → `ssl-dashboard-tab` → `ssl-proxy-config`

### Phase E — SSE Frontend (optional)
`sse-eventsource-wire` → `sse-autoreconnect` → `sse-replace-polling`

### Phase F — OmniRoute
`omniroute-integrate` — add to mcp.json, wire allowed_tools

---

## Stack & Conventions

- **Python 3.14** · **`uv`** — never `pip`
- **Tortoise ORM** + PostgreSQL (asyncpg) — `localhost:5432/cybersec_forensics`
- **Starlette ASGI** + uvicorn port 8000
- **FastMCP** for stdio MCP server (Claude Code CLI)
- **Pydantic v2**
- **cryptography** lib: Ed25519, BLAKE2b-256, Argon2id, AES-256-GCM
- **claude-agent-sdk** @ v0.1.61
- Subagents cannot call subagents — never `"Agent"` in `AgentDefinition.tools`
- SSL certs: `~/.omniroute/certs/` · Keys: `/etc/dystopian-crypto/keys`

---

## SDK Code Patterns

### Tool definition (SDK in-process format)
```python
@tool("tool_name", "description", {"param": {"type": "string"}})
async def _fn(args: dict) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(result)}]}
```

### ClaudeAgentOptions
```python
opts = ClaudeAgentOptions(
    allowed_tools=allowed,
    agents=agents,
    base_url=os.environ.get("ANTHROPIC_BASE_URL", "http://localhost:8000/v1"),
    api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
)
```

### ClaudeSDKClient (multi-turn)
```python
async with ClaudeSDKClient(options=options) as client:
    await client.query("prompt")
    async for msg in client.receive_response():
        if isinstance(msg, ResultMessage):
            session_id = msg.session_id
```

### PreToolUse hook
```python
async def audit_hook(input_data, tool_use_id, context):
    await write_scoped_entry_async(entry_type="tool_call", data=input_data)
    return {}
options = ClaudeAgentOptions(hooks={"PreToolUse": [HookMatcher(hooks=[audit_hook])]})
```

### AgentDefinition from frontmatter
```python
AgentDefinition(
    description=card.card.description,
    prompt=card.body,
    tools=card.tools or ["Read", "Glob", "Grep"],  # NEVER "Agent"
    model=card.model,
)
```

### A2A execute() → SDK
```python
async def execute(self, task, message):
    result = await run_agent_query("cybersec-analyst", self._extract_text(message))
    self._reply(task.id, result or "No response.")
```

### Hook import pattern (graceful fallback)
```python
import sys, os
_AI_HOOKS = os.environ.get("CYBERSEC_AI_HOOKS_DIR", "/home/daen/Projects/AI")
if _AI_HOOKS not in sys.path:
    sys.path.insert(0, _AI_HOOKS)
try:
    from hooks.database import (ScopeContext, write_scoped_entry_async,
        query_findings_db_async, get_recent_entries_async, get_scoped_entries_async)
    from hooks.exact_match_cache import (compute_cache_key, cache_get_async,
        cache_put_async, cache_invalidate_async, cache_analytics_async)
    _HOOKS_OK = True
except ImportError:
    _HOOKS_OK = False
```

### DB bootstrap imports
```python
from db.bootstrap import (get_database_health_async, init_tortoise_async,
    bootstrap_intelligence_async as bootstrap_intelligence_db_async)
```

### Scope helpers
Copy from `mcp_server.py` lines 16–142 into `src/mcp/cybersec/helpers.py`.

---

## Investigation Phases

| Phase | Name               | Agent                   |
|-------|--------------------|-------------------------|
| 0     | Case Opening       | cybersec-agent          |
| 1     | Reconaissance      | cybersec-agent          |
| 2     | Deep Scan          | filesystem-analyst      |
| 3     | Network Analysis   | network-analyst         |
| 4     | Persistence Hunt   | persistence-analyst     |
| 5     | Memory Forensics   | memory-analyst          |
| 6     | IOC Correlation    | cybersec-analyst        |
| 7     | Threat Attribution | threat-modeler          |
| 8     | Artifact Signing   | cybersec-agent (crypto) |

---

## NIST Fixtures (data/fixtures/)

### nist_csf_2.json — NIST CSF 2.0
**Source**: NIST reference tool XLSX (parsed via openpyxl)
- **185 subcategories**, 6 functions: GV (Govern), ID (Identify), PR (Protect), DE (Detect), RS (Respond), RC (Recover)
- Schema per entry: `id, title, function, function_description, category, category_description, implementation_examples, informative_references`
- Current SKILL.md coverage: 46 of 185 subcategories referenced
- Pending: DB model `NistCsfControl`, seed function `seed_nist_csf()`, CLI command, dashboard endpoint

### nist_ai_rmf.json — NIST AI RMF 1.0
**Source**: `https://airc.nist.gov/docs/playbook.json`
- **72 subcategories**, 4 functions: Govern, Map, Measure, Manage
- Schema per entry: `id, function, category, title, description, section_about, suggested_actions (list[str]), ai_actors, topic`
- Pending: DB model `NistAiRmfControl`, seed function `seed_nist_ai_rmf()`, CLI command, dashboard endpoint

---

## Blueprint Reference
`/home/daen/Projects/AI/blueprints/agent-sdk/` — `custom-tools.md`, `mcp.md`, `agent-loop.md`, `subagents.md`, `sessions.md`, `hooks.md`
