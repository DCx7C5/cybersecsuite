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
| `/dashboard/*`            | Dashboard UI + 30 REST + 4 SSE endpoints (36 routes total) |
| `/v1/*`                   | AI Proxy (OpenAI-compat) ← Claude routes here              |
| `/a2a/*`, `/.well-known/` | A2A JSON-RPC 2.0 server                                    |

### settings.json (`.claude/settings.json`) — 14 top-level keys
```json
{
  "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1", ... },
  "agent": "cybersec-agent",
  "version": "0.1.0",
  "asgi": { "host": "127.0.0.1", "port": 8000, "alt_port": 8080, "tls_port": 8433 },
  "mcp": { "servers": ["cybersec", "dystopian"], "tool_prefix": "mcp__" },
  "proxy": { "enabled": true, "default_strategy": "cost-optimized", "browser_providers": {...} },
  "crypto": { "algorithm": "Ed25519", "hash": "blake2b", "hash_digest_size": 32, "key_derivation": {...}, "encryption": {...} },
  "signing": { "algorithm": "Ed25519", "token_format": "frontmatter.payload", "default_expiry_hours": 8760 },
  "artifacts": { "checksum_algorithm": "blake2b", "signature_log_enabled": true },
  "keys": { "directory": "/etc/dystopian-crypto/keys", "permissions": {...} },
  "cache": { "integrity_key": "cache_integrity", "default_ttl_hours": 24 },
  "security": { "min_password_length": 32, "require_password_file": true, "audit_logging": true },
  "hooks_dir": "src/hooks/",
  "hooks": {
    "PreToolUse":        [{ "matcher": ".*", "hooks": [{"type":"command","command":"...pre_tool_call.py"}] }],
    "PostToolUse":       [{ "matcher": ".*", "hooks": [{"type":"command","command":"...post_tool_use.py"}] }],
    "Stop":              [{ "hooks": [{"type":"command","command":"...session_end.py"}] }],
    "SessionStart":      [{ "hooks": [{"type":"command","command":"...first_init.py && ...session_start.py"}] }],
    "UserPromptSubmit":  [{ "hooks": [{"type":"command","command":"...user_prompt_submit.py"}] }],
    "SubagentStart":     [{ "hooks": [{"type":"command","command":"...agent_start.py"}] }],
    "SubagentStop":      [{ "hooks": [{"type":"command","command":"...agent_end.py"}] }],
    "TeammateIdle":      [{ "hooks": [{"type":"command","command":"...termmate_idle.py"}] }],
    "PreCompact":        [{ "hooks": [{"type":"command","command":"...pre_compact.py"}] }],
    "PostCompact":       [{ "hooks": [{"type":"command","command":"...post_compact.py"}] }]
  }
}
```

**Workspace-level hooks** (10, in settings.json `hooks` key): `PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`, `UserPromptSubmit`, `SubagentStart`, `SubagentStop`, `TeammateIdle`, `PreCompact`, `PostCompact` — fire globally via Claude Code hook system.
**Agent-scoped hooks** (12, defined in `src/hooks/*.py` + `hooks.json`): `PhaseStart/End`, `InvestigationStart/End`, `IOCDiscovered`, `EvidenceCollected`, `FindingConfirmed`, `ModeSwitch`, `PermissionViolation`, `RootCommandExecuted`, `BaselineUpdated`, `ThreatDetected` — **custom event handlers** invoked via `_utils.py emit()`, NOT native Claude Code settings.json properties.
**Root src/hooks/ directory (32 .py files)**: 10 settings.json-wired + 12 programmatic event handlers + 10 utility modules.

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
| File                 | Lines | Purpose                                                                |
|----------------------|-------|------------------------------------------------------------------------|
| `mcp.json`           | ~60   | 3 MCP servers for Claude Code CLI (2 project + 1 external)             |
| `pyproject.toml`     | —     | Python 3.14, uv, all deps                                              |
| `Makefile`           | —     | `make serve`, `make test`, etc.                                        |
| `docker-compose.yml` | —     | ASGI + PostgreSQL + Redis, YAML anchors `&common`/`&db-env`/`&ai-keys` |
| `PROPOSAL.md`        | ~240  | Plugin separation architecture proposal                                |
| `PROPOSAL_MEM.md`    | ~250  | Global uncompressed claude memory cache proposal                       |

### src/
| File                    | Lines | Purpose                                                                 |
|-------------------------|-------|-------------------------------------------------------------------------|
| `src/proxy/asgi.py`     | 123   | ASGI app, env-driven ports, mounts all sub-apps, TelemetryMiddleware    |
| `src/manage.py`         | 161   | CLI management dispatcher (delegates to manage/_commands.py)            |
| `src/logger.py`         | 30    | Structured logger                                                       |
| `src/csmcp/__init__.py` | ~30   | `all_servers()` → `{cybersec, dystopian}`, `allowed_tools()` → 36 tools |

### src/csmcp/ (renamed from src/mcp/ — Phase H)
**Critical**: `src/mcp/` was renamed to `src/csmcp/` to resolve naming conflict with pip's `mcp` v1.26.0 package (needed by `claude_agent_sdk`). The original `src/mcp/` shadowed pip's `mcp` when `PYTHONPATH=src` was set. `mcp_server.py` (1288L FastMCP duplicate) was **DELETED** in Phase H.
| File                            | Lines | Purpose                                                             |
|---------------------------------|-------|---------------------------------------------------------------------|
| `__init__.py`                   | ~30   | `all_servers()` → 2 servers; `allowed_tools()` → 36 tool names     |
| `_sdk_compat.py`                | ~80   | `@tool` shim — resilience if `claude_agent_sdk` unavailable         |
| `cybersec/__init__.py`          | ~80   | Assembles 31 cybersec tools → `cybersec_server` (McpSdkServerConfig)|
| `cybersec/server.py`            | 30    | Slim stdio entry point (`python -m csmcp.cybersec.server`)          |
| `cybersec/findings.py`          | —     | add_finding, add_ioc, query_findings, update_risk_register (4)      |
| `cybersec/db.py`                | —     | db_healthcheck, bootstrap_intelligence (2)                          |
| `cybersec/intelligence.py`      | —     | suggest_mitre, get_project_memory (2)                               |
| `cybersec/layers.py`            | —     | share_to_layers, get_layer_value (2)                                |
| `cybersec/cache.py`             | —     | cache_lookup, cache_store, cache_analytics, cache_invalidate (4)    |
| `cybersec/proxy.py`             | —     | proxy_chat, proxy_providers, proxy_models, proxy_usage, proxy_cost, simulate_route, set_budget_guard, get_circuit_breakers, explain_route, routing_strategies (10) |
| `cybersec/session.py`           | —     | session_snapshot, agent_registry, best_provider (3)                 |
| `cybersec/cases.py`             | —     | case_open, case_status (2)                                          |
| `cybersec/poc.py`               | —     | add_poc, query_pocs (2)                                             |
| `dystopian.py`                  | ~200  | 5 crypto tools (Ed25519/Argon2id/AES-256-GCM)                      |
| `dystopian_server.py`           | 30    | Slim stdio entry point (`python -m csmcp.dystopian_server`)         |

### src/agent/ (new — Phase H)
High-level Claude Agent SDK integration package.
| File           | Lines | Purpose                                                         |
|----------------|-------|-----------------------------------------------------------------|
| `__init__.py`  | 14    | Public API: `AgentRunner`, `SessionManager`                     |
| `runner.py`    | ~110  | `AgentRunner` — multi-turn query(), stream(), mode prefix injection |
| `sessions.py`  | ~140  | `SessionManager` + `SessionRecord` — wraps SDK session lifecycle |
| `hooks.py`     | ~130  | 4 hooks: `security_hook`, `audit_hook`, `ioc_hook`, `cost_hook` |
| `streaming.py` | ~90   | `stream_query()` — SSE-ready async generator                    |

Usage:
```python
from agent import AgentRunner
runner = AgentRunner(agent_name="cybersec-analyst", mode="blue")
result = await runner.query("Analyse CVE-2024-1234")
# Streaming:
async for chunk in runner.stream("What are the top threats?"):
    print(chunk)  # {"type":"text","text":"..."} etc.
```

### src/a2a/
| File                | Lines | Purpose                                                                              |
|---------------------|-------|--------------------------------------------------------------------------------------|
| `agent_sdk.py`      | 250   | SDK bridge — `build_agent_options()` → 36 MCP tools (31+5) via `csmcp.all_servers()` |
| `agent_loader.py`   | 272   | Loads `.claude/agents/*.md` → AgentCards                                             |
| `orchestrator.py`   | 365   | A2A task orchestration                                                               |
| `dev_agents.py`     | 322   | Dev agent stubs (SDK-wired ✅)                                                        |
| `cybersec_agent.py` | 350   | CybersecAgent (SDK-wired ✅)                                                          |
| `server.py`         | 236   | A2A JSON-RPC server                                                                  |
| `client.py`         | 205   | A2A client                                                                           |
| `registry.py`       | 257   | AgentRegistry — remote A2A discovery                                                 |
| `task_store.py`     | 157   | In-memory + DB task store                                                            |
| `models.py`         | 215   | A2A Pydantic models                                                                  |
| `enums.py`          | —     | A2A enums                                                                            |
| `agent.py`          | —     | BaseA2AAgent                                                                         |

### src/ai_proxy/
| File                        | Lines | Purpose                                                   |
|-----------------------------|-------|-----------------------------------------------------------|
| `routes.py`                 | 224   | OpenAI-compat `/v1/*` endpoints                           |
| `providers/registry.py`     | 1163  | **60 providers**, model lists, cost metadata, auth types  |
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
| `vault.py` | ~200 | File-based encrypted secret vault |
| `cli_integration.py` | ~416 | Runnable Click CLI: ssl + vault commands |
| `template_renderer.py` | 228 | Certificate template renderer |
| `cache.py` | 270 | Crypto cache layer |
| `config.py` | 253 | Crypto configuration |

### src/db/ (44 model files, 82 model classes discovered by introspector ✅)
PostgreSQL via Tortoise ORM (asyncpg). DB: `cybersec_forensics`.
Key models: Investigation, Finding, IOC, YaraRule, NetworkEvent, ComplianceRecord, AuditLog, ApiUsageLog, A2ATask, Artifact, MitreTechnique, CVE, CAPEC, CWE, ThreatProfile, ProofOfConcept, NistCsfControl, NistAiRmfControl, and 60+ more (including junction tables).
**Fixtures**: 7 JSON files in `src/db/fixtures/` (mitre_techniques, mitre_actors, mitre_software, cwe_entries, capec_entries, cve_entries, **poc_entries**)
**Known skips**: `db.models.forensic` (SessionPhase enum missing INIT), `db.models.yara_rule` (YaraRuleSource enum missing IOC_DERIVED) — `_schema.py` silently skips these on import error.
Shell scripts: `init_db.sh`, `init_session.sh`, `backup_db.sh`.

### src/checks/ (5 files, split from single 699L file)
Integrity check module — validates model FK consistency, fixture coverage, and config file paths.
| File                | Lines | Purpose                                            |
|---------------------|-------|----------------------------------------------------|
| `integrity.py`      | 68    | Thin dispatcher: `run_all_checks()` → 3 submodules |
| `_model_check.py`   | 281   | `check_models()` — FK consistency, field validation |
| `_fixture_check.py` | 117   | `check_fixtures()` — fixture file coverage          |
| `_config_check.py`  | 254   | `check_config()` — config paths, MCP entries         |
| `_constants.py`     | —     | Shared constants (`_REPO_ROOT`, `_SRC_ROOT`, etc.) |
| `__init__.py`       | —     | Re-exports                                          |

✅ **Lint clean** — 0 ruff errors (was 40, fixed in Phase J).

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

### src/dashboard/ (36 routes, 82 model registry)
| File/Dir          | Lines | Purpose                                                              |
|-------------------|-------|----------------------------------------------------------------------|
| `routes.py`       | 63    | Thin route wiring — 36 Starlette routes                              |
| `_html.py`        | ~680  | SPA HTML + renderTable() JS component + Explorer tab                 |
| `_handlers.py`    | 8     | Re-export shim → `api/`                                              |
| `api/__init__.py` | 95    | Re-exports all 36 handlers                                           |
| `api/core.py`     | 153   | overview, providers, usage, health, crypto                           |
| `api/agents.py`   | 215   | a2a, agents, routing, factory, agent-query                           |
| `api/forensic.py` | 396   | findings, iocs, yara, network, intel, audit, compliance, NIST        |
| `api/ops.py`      | 183   | cases, tasks, task lifecycle, PoCs                                   |
| `api/tables.py`   | 148   | db counts, investigations, models, generic table, prompts, telemetry |
| `api/sse.py`      | 153   | 4 SSE streaming endpoints                                            |
| `api/page.py`     | 12    | dashboard HTML page                                                  |
| `_schema.py`      | 149   | Tortoise model introspector — 82 models, serialization, pagination   |

**New endpoints (Phase H/I)**:
- `GET /api/models` — lists all 82 registered DB models with table name + field count
- `GET /api/tables/{model}` — generic paginated query for ANY model by name (supports sort, filter_*)
- `POST /api/agent-query` — agent-sdk bridge: {agent, prompt, context_table?, row_ids?} → agent response

**Expanded endpoints** (now return full model fields, not just summaries):
findings (20 fields), iocs (14), yara (14), network (+hosts +ips), intelligence (+mitre +cve), audit (12), compliance (13), nist-csf (dynamic), nist-ai-rmf (dynamic)

Current tabs in HTML: Providers, Usage & Cost, Agents, Routing, Factory, Prompts, Health, Crypto, A2A, Investigations, DB Counts, Cases, Tasks, PoCs, **Explorer** (new — generic table viewer).
SSE: /sse/cases, /sse/tasks, /sse/health, /sse/telemetry

### .claude/ system
| Component    | Files                                                                                                                    | Status                       |
|--------------|--------------------------------------------------------------------------------------------------------------------------|------------------------------|
| `agents/`    | **34 agents** (33 specialists + AGENT_FACTORY) + DEV_SUB_AGENTS + `teams/` (3 modes) + `sub_agents/` (1: cybersec-agent) | ✅ all consistent frontmatter |
| `hooks/`     | 31 .py files — 10 settings.json-wired + 12 programmatic event handlers + 9 utility modules (legacy utils.py deleted)     | ✅ lint clean, deduplicated   |
| `commands/`  | **8 slash commands** + config.py + `__init__.py` + README.md                                                             | ⚠️ NEVER AUDITED             |
| `skills/`    | **933 SKILL.md** across 26 active domains (hardening index-only)                                                         | ✅ RESTRUCTURED               |
| `templates/` | 14 template files across 6 subdirs                                                                                       | Not reviewed                 |

#### templates/ (14 files across 6 subdirs): artifact.md, baselines/, iocs/, project/, reports/, session/, threat-intelligence/

#### hooks/ → src/hooks/ (32 .py files, consolidated from root hooks/)
**10 settings.json-wired** (Claude Code native hook system):
`pre_tool_call.py` (PreToolUse), `post_tool_use.py` (PostToolUse), `session_end.py` (Stop),
`first_init.py` + `session_start.py` (SessionStart, chained), `user_prompt_submit.py` (UserPromptSubmit),
`agent_start.py` (SubagentStart), `agent_end.py` (SubagentStop), `termmate_idle.py` (TeammateIdle),
`pre_compact.py` (PreCompact), `post_compact.py` (PostCompact)

**12 custom event handlers** (invoked via `_utils.py emit()`, NOT native Claude Code):
`investigation_end`, `investigation_start`, `phase_end`, `phase_start`,
`ioc_discovered`, `evidence_collected`, `finding_confirmed`, `mode_switch`,
`permission_violation`, `root_command_executed`, `baseline_updated`, `threat_detected`

**10 utility/support modules** (not event handlers):
`_utils`, `utils` (shared utilities), `database`, `exact_match_cache`,
`yara_rule_generator`, `yara_rule_optimizer`, `yara_rule_tester`,
`uvloop_integration`, `hooks.json` (event registry), `__init__.py`

#### commands/ — 8 slash commands
| Command        | Purpose                                       |
|----------------|-----------------------------------------------|
| `hunt`         | Check for suspicious processes and injections |
| `browser-hunt` | Browser artifact forensics                    |
| `memory-dump`  | Process injection indicators                  |
| `net-hunt`     | ARP spoofing detection                        |
| `mode-switch`  | Switch blue/red/purple mode                   |
| `setup`        | Run manage.py commands                        |
| `test-config`  | Test configuration validation                 |
| `team-task`    | Dispatch task to a blue/red/purple team       |

Supporting files: `config.py`, `__init__.py`, `README.md`

#### hooks/_utils.py — shared utilities
`ensure_structure`, `get_project_dir`, `get_session_dir`, `audit`, `emit`, `hook_context`

---

## Agent System

### `"agent": "cybersec-agent"` — Default Claude Code Agent
Loads `.claude/agents/cybersec-agent.md`. Orchestrator with `role: orchestrator`.
Accepts `blue|red|purple` mode. Delegates to all 32 specialist sub-agents.

### agents/ directory structure
```
.claude/agents/
├── <34 agent .md files>               ← all specialists + orchestrator
├── AGENT_FACTORY.md                   ← agent creation orchestrator (Opus)
├── DEV_SUB_AGENTS.md                  ← dev sub-agent reference
├── teams/                             ← blue.md, red.md, purple.md team modes
└── sub_agents/
    └── cybersec-agent.md              ← orchestrator in sub_agents context
```

### All 34 agents — frontmatter consistent ✅
Model tiers:
- **Haiku** — watchdog, command-verifier, token-optimizer
- **Sonnet** — 28 agents: all analysts, developers, layer2-7 specialists (default)
  Includes: audiovideo-analyst, certificate-analyst, code-reviewer, cpp-developer,
  cybersec-agent, cybersec-analyst, encoding-specialist, filesystem-analyst, frontend-design,
  kernel-analyst, layer2-7 specialists (×6), logfile-analyst, memory-analyst, network-analyst,
  persistence-analyst, postgres-db-engineer, process-analyst, python-developer, reverse-engineer\*,
  senior-frontend, settings-analyst, steganography-analyst, threat-modeler, vuln-scanner
- **Opus** — firmware-analyst, reverse-engineer, AGENT_FACTORY

### Two Execution Paths (NEVER conflate)
**A. Agent SDK** (internal): `query()` → `http://localhost:8000/v1` → provider routing → 36 MCP tools + subagents
**B. A2A Protocol** (external): `POST /a2a` JSON-RPC → OrchestratorAgent → registry → `execute()`

### mcp.json — 3 MCP servers for Claude Code CLI
| Key                 | Server                                                                     |
|---------------------|----------------------------------------------------------------------------|
| `cybersec`          | 31 forensics tools (`python -m csmcp.cybersec.server`, PYTHONPATH=src, uv) |
| `dystopian-crypto`  | 5 crypto tools (`python -m csmcp.dystopian_server`, PYTHONPATH=src, uv)    |
| `kerneldev`         | Kernel module dev / eBPF / symbol lookup (`kerneldev_mcp.server`, python)  |

Stale entries `token-optimization-mcp` and `playwright-stealth-mcp` **removed** (Phase I — `mcps/` dir deleted).
Both `cybersec` and `dystopian-crypto` use agent-sdk `create_sdk_mcp_server` + `mcp.server.Server` stdio transport (not FastMCP).

---

## Skills System

### Philosophy
**Skills = components** (tools, protocols, systems, software).
**Leaf directories = the specific tool/technique** applied to a component.
**Activities ≠ domains** — `red-team/`, `forensics/`, `incident-response/` are methods, not components.

### Current State (933 skills, 26 active domains)
| Type                     | Count   | Description                                              |
|--------------------------|---------|----------------------------------------------------------|
| Project-native (full)    | 170+    | Rich SKILL.md with deep taxonomy, MITRE/CWE/CVE headers  |
| Anthropic-integrated     | 752     | Full Anthropic workflow + CyberSecSuite integration      |
| **Total**                | **933** | All in `.claude/skills/`, indexed in `INDEX.md`          |

**Frontmatter** — ✅ COMPLETE (action:, mcpServers, version, license, author fields removed; single-line unquoted descriptions; Phase I.5 cleanup applied to all 933 files).

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
- **Taxonomy dirs**: CAN have hyphens (`cloud-security`, `crypto-pki`)
- **Leaf skill dirs**: Single-word only (`volatility3`, `cobaltstrike`, `kerberoasting`)
- **Deep taxonomy**: `name:` = join layers 2→last with hyphens
  - Example: `network/protocol/tcp/syn-flood/detect` → `name: protocol-tcp-syn-flood-detect`
- 224 explicit collision overrides for disambiguation

### SKILL.md Format
```yaml
---
name: skill-name
description: Single-line unquoted description text.
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

**Field inventory**: `name`+`description` (933), `model`+`maxTurns`+`tools`+`tags` (780), `mitre_attack` (644), `nist_csf` (752), `d3fend_techniques` (139), `domain`+`subdomain`+`source` (752 Anthropic), `cwe` (99), `cve` (51), `skills` (22 cross-refs).

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

## OmniRoute Integration

**Status**: PENDING (`omniroute-integrate`). External MCP at `/home/daen/Projects/OmniRoute/open-sse/mcp-server/` — 19 tools (`omniroute_*`): health, combos, metrics, route, quota, cost, catalog, simulate, budget, strategy, resilience, test, best-combo, explain + 3 skill tools. Register in `mcp.json`, env: `OMNIROUTE_API_KEY`, `OMNIROUTE_BASE_URL=http://localhost:8888`.

---

## Roadmap

### ✅ Done
- Phase 0 — agent frontmatter, ports, docker, settings, deleted dead middleware
- Phases 1-7 — config, intel seeds, docs, skills taxonomy, domain restructuring, team task, vault/SSL/fixtures/checks/providers
- Phase A — MCP split: `src/csmcp/cybersec/` (31 tools) + `dystopian.py` (5 tools) → 36 total
- Phase A2 — A2A stubs wired to SDK
- Phase D — Telemetry stack complete
- Phase D.5 — PoC table (model, seeds, CLI, MCP tools, dashboard tab)
- Phase E.1 — Type safety fixes
- Phase F — File splitting (`intel_loader`, `routes.py`, `registry.py`, `manage.py`, `integrity.py`)
- Phase H — `mcp_server.py` DELETED, agent-sdk migration complete, `src/csmcp/` rename, `src/agent/` package created
- Phase I — Tool inventory (`docs/tools.md`), MEMORY.md sync, `mcp.json` cleanup (stale entries removed)
- Phase I.6 — All 10 hooks wired to settings.json (was 3); 3 new scripts created
- Phase J — All 72 ruff lint errors → 0; hooks/ deduplicated to src/hooks/; dead code removed
- Phase K.1 — `renderTable()` JS component + Explorer tab (sortable, searchable, paginated, type-aware)
- Phase K.2 — Cases + Tasks tabs converted to `renderTable`; PoCs tab panel added (stat cards + table); api/pocs fetch wired
- Phase K.3 — Providers, Usage, Crypto, A2A tabs converted from raw innerHTML tables to `renderTable`
- Phase L — `src/agent/` package: runner.py, sessions.py, hooks.py, streaming.py all complete
- Phase M.1 — `_handlers.py` (1228L) split into `dashboard/api/` package (7 modules, 36 handlers)
- Dashboard expansion — 36 routes, 82-model registry, generic table endpoint, agent-query bridge, expanded handlers
- Skills taxonomy — 933 SKILL.md across 26 domains, 752 Anthropic-integrated, frontmatter cleaned
- Provider expansion — 60 providers in `registry.py`
- 34 agents total (33 specialists + AGENT_FACTORY)

### docs/ — 10 files
`architecture.md`, `api.md`, `agents.md`, `configuration.md`, `contributing.md`, `deployment.md`, `mcp-tools.md`, `quickstart.md`, `teams.md`, `tools.md`

---

## Active Roadmap (Current)

### Phase K — Dashboard Full Buildout (in progress)
1. ✅ `renderTable()` JS component + Explorer tab
2. ✅ Cases + Tasks converted to renderTable; PoCs tab panel added
3. ✅ Providers, Usage, Crypto, A2A converted to renderTable
4. Add new tabs: forensic sessions, MITRE, intel feeds, artifacts, machines, baselines, vulns...
5. Interactive agent query panel (SSE streaming, agent selection, context enrichment)
6. Settings dashboard (read/edit settings.json)
7. Team builder + Task chain builder; Agent manager; Skill browser; Hook manager

### Phase M — Code Splits (in progress)
1. ✅ Split `_handlers.py` → `dashboard/api/` package
2. `_commands.py` (484L) — kept as-is (manageable)
3. Fix checks/, registry, consolidate a2a/ — pending

### Phase N — Documentation
Update all 10 docs + MEMORY.md + README.md to reflect current state

### Queued / Optional
- Phase G — SSE Frontend: `sse-eventsource-wire` → `sse-autoreconnect` → `sse-replace-polling`
- OmniRoute integration: add to mcp.json + wire allowed_tools
- Phase E — Asset sync from Anthropic source (deferred)

---

## Stack & Conventions

- **Python 3.14** · **`uv`** — never `pip`
- **Tortoise ORM** + PostgreSQL (asyncpg) — `localhost:5432/cybersec_forensics`
- **Starlette ASGI** + uvicorn port 8000
- **agent-sdk** (`create_sdk_mcp_server`) for MCP tools (in-process); `mcp.server.Server` for stdio transport
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
Already in `src/csmcp/cybersec/helpers.py` — `ScopeState`, `_build_scope_context()`, `_coerce_limit()`, etc.

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
- ✅ DB model `NistCsfControl`, seed function `seed_nist_csf()`, CLI command `seed-nist-csf`, dashboard endpoint `/api/nist-csf`

### nist_ai_rmf.json — NIST AI RMF 1.0
**Source**: `https://airc.nist.gov/docs/playbook.json`
- **72 subcategories**, 4 functions: Govern, Map, Measure, Manage
- Schema per entry: `id, function, category, title, description, section_about, suggested_actions (list[str]), ai_actors, topic`
- ✅ DB model `NistAiRmfControl`, seed function `seed_nist_ai_rmf()`, CLI command `seed-nist-ai-rmf`, dashboard endpoint `/api/nist-ai-rmf`

---

## Blueprint Reference
`/home/daen/Projects/AI/blueprints/agent-sdk/` — `custom-tools.md`, `mcp.md`, `agent-loop.md`, `subagents.md`, `sessions.md`, `hooks.md`
