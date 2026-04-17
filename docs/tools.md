# CyberSecSuite — Complete Tool Inventory

**Last updated:** Phase I (2026-04-17)  
**Total tools:** 54 (15 builtins + 36 MCP + 3 external/stale)

---

## 1. Claude Code Built-in Tools (15 global)

Always available in Claude Code. No configuration needed.

| Tool | Type | Purpose |
|------|------|---------|
| `Bash` | shell | Execute shell commands (Unix/Linux/macOS) |
| `Read` | file | Read file contents (text or binary) |
| `Write` | file | Create new files with content |
| `Edit` | file | Edit file contents with find-replace |
| `MultiEdit` | file | Batch edit multiple files in one call |
| `Glob` | file | Fast file pattern matching (glob syntax) |
| `Grep` | search | Fast regex search in files (ripgrep) |
| `LS` | file | List directory contents with metadata |
| `WebSearch` | web | Search the public internet |
| `WebFetch` | web | Fetch URL content as markdown or raw HTML |
| `Agent` | meta | Delegate to another Claude Code agent |
| `TodoRead` | meta | Read workspace todo list |
| `TodoWrite` | meta | Write to workspace todo list |
| `NotebookRead` | meta | Read workspace notebook |
| `NotebookEdit` | meta | Edit workspace notebook |

---

## 2. Project MCP Tools — Cybersec Server (31 tools)

**Location:** `src/csmcp/cybersec/` (31 tools via claude_agent_sdk)  
**Transport:** stdio via `python -m csmcp.cybersec.server`  
**Prefix:** `mcp__cybersec__`  
**Module prefix in code:** `csmcp.cybersec.*`

### 2.1 Findings Module (4 tools)
- `add_finding` — Add a new security finding to scoped store (file + DB)
- `add_ioc` — Add/merge IOC (indicator of compromise) into scoped memory + DB
- `query_findings` — Query findings with severity/status filters
- `update_risk_register` — Update risk register with impact, likelihood, mitigation

### 2.2 Database Module (2 tools)
- `db_healthcheck` — Check PostgreSQL/Tortoise health + optional table counts
- `bootstrap_intelligence` — Bootstrap NVD/CVE, CWE, CAPEC, MITRE families

### 2.3 Intelligence Module (2 tools)
- `suggest_mitre` — Suggest MITRE ATT&CK techniques from behavior description
- `get_project_memory` — Return project memory: findings, IOCs from current scope

### 2.4 Layers Module (2 tools)
- `share_to_layers` — Share value to workspace/project/session scopes
- `get_layer_value` — Read values from scope layer

### 2.5 Cache Module (4 tools)
- `cache_lookup` — Deterministic exact-match cache lookup
- `cache_store` — Store tool call result in exact-match cache
- `cache_analytics` — Return cache hit/miss statistics
- `cache_invalidate` — Invalidate cache entries by key prefix/tag/tool

### 2.6 Proxy Module (10 tools)
- `proxy_chat` — Route chat completion through AI proxy with fallback
- `proxy_providers` — List all configured AI providers + status
- `proxy_models` — List all available models across providers
- `proxy_usage` — Return AI proxy usage summary (tokens, costs)
- `proxy_cost` — Return detailed cost breakdown by provider
- `simulate_route` — Dry-run route simulation (show provider/model choice)
- `set_budget_guard` — Set spending budget guard
- `get_circuit_breakers` — Return circuit breaker status for all targets
- `explain_route` — Explain step-by-step provider/model selection
- `routing_strategies` — List all available routing strategies

### 2.7 Session Module (3 tools)
- `session_snapshot` — Return full session state (scope, usage, budget, circuit breakers)
- `agent_registry` — List all registered A2A agents
- `best_provider` — Find best provider/model for a task

### 2.8 Cases Module (2 tools)
- `case_open` — Open new investigation case (Phase 0)
- `case_status` — Get status of current or specific case

### 2.9 PoC Module (2 tools)
- `add_poc` — Add new PoC exploit record linked to CVE
- `query_pocs` — Query PoC records filtered by CVE/status/weaponized

---

## 3. Project MCP Tools — Dystopian-Crypto Server (5 tools)

**Location:** `src/csmcp/dystopian.py` (5 tools via claude_agent_sdk)  
**Transport:** stdio via `python -m csmcp.dystopian_server`  
**Prefix:** `mcp__dystopian__`  
**Module prefix in code:** `csmcp.dystopian.*`

| Tool | Purpose |
|------|---------|
| `crypto_generate_keypair` | Generate Ed25519 CA/signing keypair (Argon2id+AES-256-GCM) |
| `crypto_sign_artifact` | Sign artifact (file/bytes) with Ed25519 private key |
| `crypto_verify_artifact` | Verify Ed25519-signed artifact token |
| `crypto_list_keys` | List all managed Ed25519 key pairs + metadata |
| `crypto_rotate_key` | Rotate existing Ed25519 key (re-encrypt with new key) |

---

## 4. Agent SDK In-Process Tools (42 total: 6 builtins + 36 MCP)

**Context:** When using `query()` from `claude_agent_sdk` via `src/a2a/agent_sdk.py`  
**Default builtins:** `Read`, `Glob`, `Grep`, `Bash`, `Agent`, `WebSearch` (6)  
**Optional builtins:** `Write`, `Edit` (can be passed as `extra_tools`)  
**MCP tools:** All 36 from servers #2 and #3 (cybersec + dystopian)  
**Total:** 6 + 36 = 42 tools

### 4.1 Agent SDK Builtin Tools (6 default + 2 optional)

Same as Claude Code builtins but scoped to agent session.

**Default:** Read, Glob, Grep, Bash, Agent, WebSearch  
**Optional:** Write, Edit

### 4.2 Agent SDK MCP Tools (36)

**Cybersec:** 31 tools (prefixed `mcp__cybersec__*`)  
**Dystopian:** 5 tools (prefixed `mcp__dystopian__*`)

All MCP tools listed in sections 2 and 3 above are available in-process.

---

## 5. External MCPs (Project-Local, via mcp.json)

**Location:** `mcp.json` (workspace-level)  
**Transport:** stdio via `mcp.json` command entries

### 5.1 KernelDev MCP ✅ (Active)
- **Source:** External pip package `kerneldev-mcp`
- **Command:** `python -m kerneldev_mcp.server`
- **Tools:** Kernel module dev, eBPF analysis, kernel symbol lookup
- **Status:** ✅ Functional (external dependency)

### 5.2 Token Optimization MCP ❌ (Stale)
- **Source:** `mcps/token-optimization-mcp/` (directory deleted)
- **Status:** ❌ Non-functional (mcps/ removed)
- **Last seen:** token counting, prompt compression, semantic caching
- **Replacement:** Consider integrating token limits into agent_sdk.py

### 5.3 Playwright Stealth MCP ❌ (Stale)
- **Source:** `mcps/playwright-stealth-mcp/` (directory deleted)
- **Status:** ❌ Non-functional (mcps/ removed)
- **Last seen:** Headless Brave browser, fingerprint spoofing
- **Replacement:** Consider using `WebFetch` or external browser service

---

## 6. Tool Availability Matrix

| Scope | Builtins | MCP | Total | Context |
|-------|----------|-----|-------|---------|
| Claude Code CLI | 15 | 36 (cybersec+dystopian) | 51 | Global, all agents |
| Agent SDK in-process | 6-8 | 36 (cybersec+dystopian) | 42-44 | Per session |
| Dashboard handlers | N/A | 36 via SDK | 36 | Via /api/agent-query |
| A2A orchestrator | 6 | 36 via SDK | 42 | Via /a2a JSON-RPC |

---

## 7. Integration Points

### 7.1 Claude Code CLI
```bash
# All 51 tools available via mcp.json
# cybersec + dystopian servers auto-start
# User prompts can call mcp__* tools directly
```

### 7.2 Agent SDK (Python)
```python
from agent import AgentRunner
from a2a.agent_sdk import build_agent_options

runner = AgentRunner(agent_name="cybersec-analyst")
result = await runner.query("Analyze CVE-2024-1234")
# Uses 42 tools (6 builtins + 36 MCP)
```

### 7.3 Dashboard REST API
```bash
POST /api/agent-query
# Streams agent responses via SSE
# Tools injected via build_agent_options()
```

### 7.4 A2A JSON-RPC Server
```bash
POST /a2a
# Orchestrator delegates to sub-agents
# Each sub-agent gets full tool suite
```

---

## 8. Tool Categories by Capability

### Findings & IOCs
- `add_finding`, `add_ioc`, `query_findings`, `update_risk_register`

### Database & Intelligence
- `db_healthcheck`, `bootstrap_intelligence`, `suggest_mitre`, `get_project_memory`

### Scope & Layers
- `share_to_layers`, `get_layer_value`

### Caching
- `cache_lookup`, `cache_store`, `cache_analytics`, `cache_invalidate`

### AI Proxy & Routing
- `proxy_chat`, `proxy_providers`, `proxy_models`, `proxy_usage`, `proxy_cost`, `simulate_route`, `set_budget_guard`, `get_circuit_breakers`, `explain_route`, `routing_strategies`

### Session & Discovery
- `session_snapshot`, `agent_registry`, `best_provider`

### Case Management
- `case_open`, `case_status`

### Exploits
- `add_poc`, `query_pocs`

### Cryptography
- `crypto_generate_keypair`, `crypto_sign_artifact`, `crypto_verify_artifact`, `crypto_list_keys`, `crypto_rotate_key`

### Shell & Files (Builtin)
- `Bash`, `Read`, `Write`, `Edit`, `MultiEdit`, `Glob`, `Grep`, `LS`

### Web (Builtin)
- `WebSearch`, `WebFetch`

### Meta (Builtin)
- `Agent`, `TodoRead`, `TodoWrite`, `NotebookRead`, `NotebookEdit`

---

## 9. Maintenance Notes

**Phase H Summary:**
- Deleted `mcp_server.py` (1288L FastMCP duplicate)
- Renamed `src/mcp/` → `src/csmcp/` (fixes naming conflict with pip's `mcp` package)
- Created `src/csmcp/cybersec/server.py` (30L slim stdio server)
- Created `src/csmcp/dystopian_server.py` (30L slim stdio server)
- Updated `mcp.json` to use new `csmcp` module paths

**Phase I Summary:**
- Removed stale `token-optimization-mcp` and `playwright-stealth-mcp` (mcps/ directory deleted)
- Kept `kerneldev` (external pip package, still functional)
- Created this tool inventory (`docs/tools.md`)
- Synchronized `MEMORY.md` with Phase H/I changes
