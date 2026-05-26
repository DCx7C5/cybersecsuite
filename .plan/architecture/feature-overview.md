# CyberSecSuite — Feature Inventory

**Verified**: 2026-05-26
**Source**: `src/css/modules/` (34 current directories), `src/css/api_services/`
(24 provider directories), `src/css/core/`, local owner Markdown, and
`.plan/session.db` (927 todos, 42 named phases)

**Status Legend**: ✅ DONE/REMOVED/CLEANED · 🟡 PARTIAL RUNTIME · 🔧 IN PROGRESS · 📋 PLANNED · ⏳ PENDING · ⚠️ BLOCKED

**Interpretation**: feature rows describe source reality and retained design
scope. `.plan/session.db` remains authoritative for live todo status; local
`src/css/**/*.md` files own implementation contracts.

## Source TODO Audit

An explicit `TODO`/`FIXME`/`XXX`/`HACK` scan of active Python source
(`src/css/`, excluding `src/legacy/`) found 41 markers on 2026-05-25.
`pass` and `NotImplementedError` were reviewed separately because protocols,
exceptions, and non-fatal cleanup paths are not automatically missing work.

| Owner area | Explicit markers | High-signal outstanding contract |
|------------|-----------------:|----------------------------------|
| `core/rag_vector` | 11 | authorization enforcement, pgvector semantic search, tag relation |
| `core/auth` + `core/accounts` | 6 | credential/token authorization and password-manager wiring |
| `api_services` | 4 | YAML-driven provider metadata and model discovery |
| other `core` owners | 9 | capabilities/config/model/permission/event consolidation |
| business modules | 11 | evidence auth/integrity, scheduling, tool typing and agent execution |

These markers are implementation evidence to reconcile against tracker todos;
they are not new completion claims.

---

## 1. Multi-Orchestrator Engine

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Orchestrator Pool Mgmt** | ✅ DONE | 1 | N concurrent orchestrators per session (spawn/kill/list/health) |
| **Pull-Based Task Queue** | ✅ DONE | 1 | Atomic `SELECT ... FOR UPDATE` pull, no duplicate execution |
| **Heartbeat Monitoring** | ✅ DONE | 1 | Periodic liveness checks, stale orchestrator detection |
| **Crash Detection & Recovery** | ✅ DONE | 1 | Auto-reassign tasks from crashed orchestrators |
| **Health Metrics Collection** | ✅ DONE | 1 | Latency, throughput, error rate per orchestrator |
| **Load Balancing** | ✅ DONE | 1 | Round-robin, least-busy, weighted strategies |
| **Atomic Result Merging** | ✅ DONE | 1 | Idempotent result collection with conflict resolution |
| **Task Lifecycle Manager** | ✅ DONE | 0 | State machine: pending→active→paused→completed |
| **Priority Scheduler** | ✅ DONE | 0 | Weighted priority queue for task ordering |
| **Team-Based Parallelisation** | 📋 PLANNED | 30 | Subprocess team spawning, TeamLeader/TeamMember roles |
| **Async Generator Pipeline** | 🟡 PARTIAL RUNTIME | 6 | `core.pipeline` plus chat `classify -> route -> execute -> observe` exists; complete runtime verification remains |
| **Session Run Modes** | 📋 PLANNED | 19 | dev/red_team/review modes with process layouts |
| **Planner Orchestrator** | 📋 PLANNED | 21+ | Separate process for architecture planning/analysis |

---

## 2. Team & Session Management

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Team ORM Model** | ✅ DONE | 0 | Tortoise model with status, config, quotas |
| **Team Lifecycle** | ✅ DONE | 0 | Create/pause/resume/completion state machine |
| **Team Quota Enforcement** | ✅ DONE | 0 | Resource limits per team (tasks, agents, storage) |
| **TaskAssignment ORM** | ✅ DONE | 0 | FK to team, priority, timeout, payload isolation |
| **Team-Centric Orchestrator Pool** | ✅ DONE | 0 | Orchestrators bound to teams, isolated result aggregation |
| **Results Isolation** | ✅ DONE | 0 | Per-team result storage, no cross-team leakage |
| **Team Metrics** | ✅ DONE | 0 | Task throughput, completion rates, resource usage |
| **Session Manager** | 📋 PLANNED | 19 | Lifecycle: create/resume/end, state machine, mode-driven layout |
| **Session Persistence** | 📋 PLANNED | 19 | PostgreSQL-backed session state (survives restart) |
| **Session Isolation & Working Dir** | 📋 PLANNED | 15 | `~/.css/sessions/<sid>/` with PathGrant permissions |

---

## 3. LLM Provider Access (Multi-Provider)

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **UniversalLLMClient** | ✅ DONE | 2 | Single entry point for all LLM calls, registry + lazy-load router |
| **SDK Registry** | ✅ DONE | 2 | Thread-safe provider→SDK routing, concurrent init protection |
| **24 Provider SDK Stubs** | ✅ DONE | 2 | anthropic, openai, gemini, groq, mistral, ollama, openrouter, cohere, ai21, together, github + 13 pending |
| **Unified Response Layer** | ✅ DONE | 2 | CSSResponse dataclass, streaming support |
| **Unified Provider SDK Arch** | 📋 PLANNED | 10 | Four adapter types: NativeSDK, HttpProvider, Ollama, BrowserRelay |
| **YAML Provider Specs** | 📋 PLANNED | 6 | Replace 4800 LOC Python with 24 declarative YAML + 1 generic adapter |
| **LLMAdapter Protocol** | 📋 PLANNED | 10 | `complete()`, `stream()`, `count_tokens()`, `caching_capability` |
| **OllamaAdapter** | 📋 PLANNED | 10 | Merges 3 existing files, uses `/api/chat` directly |
| **BrowserRelayAdapter** | 📋 PLANNED | 10 | Inject prompts into browser LLM UIs via Chrome extension |
| **Native Anthropic Adapter** | 📋 PLANNED | 10 | SDK features: prompt_caching, computer_use, extended_thinking |
| **Native OpenAI Adapter (opt)** | 📋 PLANNED | 10 | Optional: Assistants API, strict structured output |
| **Provider Routing & Resilience** | 📋 PLANNED | 13 | Circuit breaker, rate limiter, budget guard, usage tracker |
| **13 Routing Strategies** | 📋 PLANNED | 13 | Priority, round-robin, cost-optimized, weighted, P2C, LKGP, etc. |
| **11-Tier Model Routing** | 📋 PLANNED | 13 | LOCAL_MINIMAL through terminal S_PLUS with cost, complexity, hardware awareness |
| **Qwen3 Triage Router** | 📋 PLANNED | 21 | 5-tier complexity analysis, provider selection, fallback chains |

---

## 4. Prompt Caching

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **PromptCacheManager** | 📋 PLANNED | 11 | Orchestrates all 3 caching tiers transparently |
| **Tier 1: Redis Exact-Match** | 📋 PLANNED | 11 | SHA256 key on `provider+model+messages+params` → zero API cost on hit |
| **Tier 2a: Anthropic Native** | 📋 PLANNED | 11 | Automatic top-level cache_control + optional explicit breakpoints |
| **Tier 2b: OpenAI/DeepSeek Auto** | 📋 PLANNED | 11 | Automatic prefix caching, parses native cache usage fields |
| **Tier 2c: Gemini Resource** | 📋 PLANNED | 11 | `cachedContent` create/resolve/reuse via REST |
| **Tier 3: Semantic (future)** | ⏳ PENDING | 13+ | Embedding similarity for "close enough" prior responses |
| **Cache Cost Savings Tracker** | 📋 PLANNED | 11 | `estimated_savings_usd` per response, emitted to OpenObserve |
| **CachingCapability Metadata** | 📋 PLANNED | 11 | Per-adapter enum: NONE / NATIVE_AUTO / NATIVE_AUTO_EXPLICIT / NATIVE_RESOURCE |

---

## 5. QoL Output Controls

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **8 Output Toggles** | 📋 PLANNED | 12 | no_thinking, no_chat, minimal, file_only, no_markdown, structured_only, redact_secrets, append_audit_trail |
| **5 Builtin Presets** | 📋 PLANNED | 12 | silent, code-only, structured, audit, plain-text |
| **Dangerous Combo Validation** | 📋 PLANNED | 12 | Blocks 3 conflicting toggle combinations |
| **QoLInjector Service** | 📋 PLANNED | 12 | System prompt injection + fragment cache (TTL 300s) |
| **Scope Cascade** | 📋 PLANNED | 12 | session→project→global with per-agent preset binding |
| **A2A Toggle Propagation** | 📋 PLANNED | 12 | Cross-agent toggle sync via dispatcher |
| **Toggle-Hash Cache Key** | 📋 PLANNED | 12 | blake2b hash in PromptCacheManager key |

---

## 6. Agent System

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Agent ORM Model** | ✅ DONE | 0+ | Tortoise model with config, provider binding |
| **Agent Types** | ✅ DONE | 0+ | AgentConfig, AgentAssignment structs |
| **BaseAgent Protocol** | 📋 PLANNED | 8 | `AgentExecutor.execute()` → capability check → adapter → result |
| **Agent Execution Loop** | 📋 PLANNED | 8 | Tool-calling loop: parse `tool_calls` → execute → continue LLM call |
| **Agent Memory Integration** | 📋 PLANNED | 20 | ContextAssembler: sliding window + token budget + pg cold storage |
| **Agent-to-Agent Comms (A2A)** | 📋 PLANNED | 8+ | Internal dispatch via Redis, team delegation wire-up |
| **Agent Skill Execution** | 📋 PLANNED | 8 | BaseSkill.execute() via SkillRegistry |
| **Agent Observability** | 📋 PLANNED | 14 | `@instrument("agent.run")` decorator with correlation_id |
| **Forensic Analyzer Agent** | 📋 PLANNED | 29 | Cybersec-specific agent type for evidence analysis |
| **Scanner Agent** | 📋 PLANNED | 29 | Orchestrated agent teams for vulnerability scanning |

---

## 7. Tool System

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **ToolRegistry** | ✅ DONE | 2+ | 475 LOC: in-memory cache, startup discovery, provider data |
| **Tool ORM Model** | ✅ DONE | 2+ | Persisted tool definitions with provider associations |
| **ToolSpec / ToolSchema** | ✅ DONE | 2+ | Structured tool metadata with JSON Schema |
| **Builtin Provider Tools** | 📋 PLANNED | 16 | Anthropic: computer_use, bash, text_editor; OpenAI: code_interpreter, file_search |
| **Tool Calling Loop** | 📋 PLANNED | 8 | Parse `tool_calls`, execute, feed back to LLM, continue |
| **Three-Ring Architecture** | 📋 PLANNED | 9 | Service functions → (Manager OR Registry), never skip a layer |
| **Tortoise Custom Managers** | 📋 PLANNED | 9 | `ToolModel.objects = ToolManager()` with `by_provider()`, `for_team()` |
| **MCP Tool Bridge** | 📋 PLANNED | 22 | McpToolBridge pushes MCP tools into ToolRegistry as ToolType.MCP |

---

## 8. MCP Protocol Layer

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **McpRuntimeRegistry** | 📋 PLANNED | 22 | Server config, transport connect/disconnect, discovery |
| **McpClient** | 📋 PLANNED | 22 | Unified async transport wrapper (PYTHON_DIRECT / STDIO / SSE / STREAMABLE_HTTP) |
| **PYTHON_DIRECT Transport** | 📋 PLANNED | 22 | In-process FastMCP for trusted local cybersec servers |
| **McpToolBridge** | 📋 PLANNED | 22 | Server-scoped MCP tool IDs → ToolRegistry bridge |
| **MCP REST API** | 📋 PLANNED | 22 | CRUD / connect / discovery / call endpoints |
| **ASGI Startup Wire** | 📋 PLANNED | 22 | Auto-restore connections + tool sync at boot |
| **Builtin Local MCP Servers** | 📋 PLANNED | 22 | Native cybersec MCP registration (SIEM connectors, etc.) |
| **Marketplace Integration** | 📋 PLANNED | 22 | MCP server install/enable from marketplace |
| **SIEM/EDR Integration** | 📋 PLANNED | 37 | External SIEM/EDR → MCP → normalization → analysis |

---

## 9. Skills Framework

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **SkillRegistry** | ✅ DONE | 2+ | 181 LOC: skill discovery, registration, lifecycle |
| **Skill ORM Model** | ✅ DONE | 2+ | Tortoise model with skill metadata |
| **Skill Enums** | ✅ DONE | — | SkillStatus, SkillCategory |
| **BaseSkill.execute()** | 📋 PLANNED | 8 | Execution interface for registered skills |
| **Skill→Marketplace Bridge** | 📋 PLANNED | 9 | Skills registered as Marketplace items |
| **Three-Ring Cleanup** | 📋 PLANNED | 9 | Extract DB writes to SkillModel objects, Registry = cache only |

---

## 10. Tags

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Tag Manager** | ✅ DONE | 2+ | CRUD operations with in-memory dict (needs migration) |
| **Tag ORM Model** | ✅ DONE | 2+ | Tortoise model, FK relationships |
| **Tag Enums** | ✅ DONE | — | TagColor enum for visual distinction |
| **TagManager→Tortoise Migration** | 📋 PLANNED | 9 | Replace in-memory dict with custom Tortoise Manager |
| **Color-Coded Tag UI** | 📋 PLANNED | 18+ | Tag display with color indicators in frontend |

---

## 11. Incidents & Response

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Incident ORM Model** | ✅ DONE | — | Tortoise model: lifecycle, severity, status, timeline |
| **Incident Types** | ✅ DONE | — | Incident dataclasses with metadata |
| **Incident Enums** | ✅ DONE | — | IncidentStatus, Severity, IncidentType |
| **Incident Lifecycle** | 📋 PLANNED | 29 | Create/track/close/timeline management |
| **Evidence Chain-of-Custody** | 📋 PLANNED | 29 | Immutable EvidenceChain via EventStore, hash-verified, collector-attributed |
| **Alert→Incident Promotion** | 📋 PLANNED | 29 | Threshold-based auto-promotion from alerts to incidents |
| **Incident→Report Pipeline** | 📋 PLANNED | 32 | Structured findings → formatted reports |

---

## 12. Threat Intelligence & MITRE ATT&CK

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Threat Intel ORM Model** | ✅ DONE | — | IOC tracking model |
| **Threat Intel Types** | ✅ DONE | — | IOC, TTP, threat-actor structs |
| **Threat Intel Enums** | ✅ DONE | — | IOCType, ThreatLevel, Confidence |
| **IOC Tracking** | 📋 PLANNED | 29 | IP/domain/hash/URL indicators of compromise |
| **Threat Feed Ingestion** | 📋 PLANNED | 29 | MISP, OTX, VirusTotal feed pulls |
| **MITRE ATT&CK Framework** | 📋 PLANNED | 29 | Tactic/technique/procedure mapping |
| **MITRE→GraphRAG Projection** | 📋 PLANNED | 29 | ATT&CK entities projected into Neo4j for attack-path traversal |
| **CVE Feed Integration** | 📋 PLANNED | 20 | Vulnerability intelligence ingestion → RAG knowledgebase |

---

## 13. Vulnerability Scanning

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Scan ORM Model** | ✅ DONE | — | Target, findings, status tracking |
| **Scan Types** | ✅ DONE | — | ScanConfig, ScanTarget, ScanFinding |
| **Scan Enums** | ✅ DONE | — | ScanStatus, ScanType, Severity |
| **Target→Agent Team→Findings Pipeline** | 📋 PLANNED | 29 | Orchestrated scan lifecycle bridging triage, teams, reports |
| **Scheduled Scans** | 📋 PLANNED | 25 | Cron-driven periodic vulnerability assessment |
| **Finding→Incident Promotion** | 📋 PLANNED | 29 | Auto-create incidents from critical findings |

---

## 14. SIEM / EDR Integration

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **SIEM Module Stub** | ✅ DONE | — | Module structure with types, enums, models |
| **Three-Store Pipeline** | 📋 PLANNED | 37 | OpenObserve(raw) → PostgreSQL(curated) → Neo4j(graph) |
| **SiemIngestService** | 📋 PLANNED | 37 | Consume external SIEM/EDR data through MCP runtime |
| **SecurityEvent Normalization** | 📋 PLANNED | 37 | Normalize connector payloads into standard format |
| **SiemAnalyzerAgent** | 📋 PLANNED | 37 | Correlate telemetry with GraphRAG + VectorRAG context |
| **Response Playbooks** | 📋 PLANNED | 37 | Workflow-driven automated response with approval gates |
| **Connector Actions via MCP** | 📋 PLANNED | 37 | Call connector actions back through MCP runtime tools |

---

## 15. Alerts & Notifications

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Alert ORM Model** | ✅ DONE | — | AlertRule, AlertDispatch config |
| **Alert Types** | ✅ DONE | — | AlertConfig, AlertPayload, AlertChannel |
| **Alert Enums** | ✅ DONE | — | AlertSeverity, AlertStatus, ChannelType |
| **Alert Dispatchers** | 📋 PLANNED | 25 | Email, Slack, Webhook output channels |
| **Event-Driven Triggers** | 📋 PLANNED | 25 | EventStore DomainEvents → AlertRule matching → dispatch |
| **Alert→Incident Escalation** | 📋 PLANNED | 29 | Threshold-based incident creation from alerts |
| **Scheduler Integration** | 📋 PLANNED | 25 | Cron-driven alert evaluation and suppression windows |

---

## 16. Evidence Management

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Evidence ORM Model** | ✅ DONE | — | Chain-of-custody: source, collector, hash, metadata |
| **Evidence Types** | ✅ DONE | — | EvidenceItem, EvidenceChain, CustodyRecord |
| **Evidence Enums** | ✅ DONE | — | EvidenceStatus, EvidenceType, CustodyAction |
| **Immutable EvidenceChain** | 📋 PLANNED | 29 | Append-only via EventStore, cryptographic hash links |
| **Collector Attribution** | 📋 PLANNED | 29 | Every evidence item attributed to collector agent |
| **Hash Verification** | 📋 PLANNED | 29 | Integrity checks on evidence retrieval |

---

## 17. Reports

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **ReportRecord Scaffold** | 🟡 PARTIAL RUNTIME | 32 | Current record stores title/type/source/content; lifecycle and artifact models remain planned |
| **ReportGenerator Scaffold** | 🟡 PARTIAL RUNTIME | 32 | Synchronous Markdown/HTML output exists; real PDF/JSON artifacts remain planned |
| **Report Endpoint Scaffold** | 🟡 PARTIAL RUNTIME | 32 | Inline create/list/get exists; queued/status/artifact/template API remains planned |
| **Multi-Format Output** | 📋 PLANNED | 32 | Markdown / HTML / PDF rendering pipeline |
| **Incident→Report Pipeline** | 📋 PLANNED | 32 | Structured findings → formatted report |
| **Compliance Reports** | 📋 PLANNED | 32 | NIST CSF / SOC2 / ISO27001 coverage reports |
| **Scheduled Report Generation** | 📋 PLANNED | 32 | Cron-driven report production |

---

## 18. Compliance & Audit

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Compliance ORM Model** | ✅ DONE | — | Framework, control, mapping entities |
| **Compliance Types** | ✅ DONE | — | ComplianceFramework, Control, Coverage |
| **Compliance Enums** | ✅ DONE | — | Framework, ControlStatus, ComplianceLevel |
| **NIST CSF / SOC2 / ISO27001 Mapping** | 📋 PLANNED | 29 | Control mapping with coverage percentage |
| **Scan→Incident→Compliance Pipeline** | 📋 PLANNED | 29 | Findings map to controls automatically |
| **Audit Trail (CQRS EventStore)** | 📋 PLANNED | 6 | Immutable event log for forensic replay |

---

## 19. Webhooks

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Webhook ORM Model** | ✅ DONE | — | URL, secret, event filters, retry config |
| **Webhook Types** | ✅ DONE | — | WebhookConfig, WebhookDelivery, WebhookPayload |
| **Webhook Enums** | ✅ DONE | — | WebhookStatus, DeliveryMethod, RetryStrategy |
| **Outbound Webhook Delivery** | 📋 PLANNED | 25 | HMAC-SHA256 signing + retry with backoff |
| **SIEM/SOAR Integration** | 📋 PLANNED | 25 | Splunk, Elastic, PagerDuty outbound events |
| **EventStore→Webhook Bridge** | 📋 PLANNED | 25 | DomainEvent subscription triggers webhook dispatch |

---

## 20. Scheduler

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Scheduler ORM Model** | ✅ DONE | — | Cron expression, task binding, status |
| **Scheduler Types** | ✅ DONE | — | ScheduleConfig, ScheduledTask, ExecutionRecord |
| **Scheduler Enums** | ✅ DONE | — | TaskType enum |
| **Cron-Style Scheduling** | 📋 PLANNED | 25 | APScheduler-based periodic execution |
| **Use Cases** | 📋 PLANNED | 25 | Periodic scans, daily threat feed sync, scheduled red-team drills, report generation |
| **Scheduler→Workflow Bridge** | 📋 PLANNED | 25 | Trigger workflow execution on schedule |

---

## 21. Workflows

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Workflow ORM Model** | ✅ DONE | — | Step definitions, state, transitions |
| **Workflow Types** | ✅ DONE | — | WorkflowDef, WorkflowStep, WorkflowState |
| **Workflow Enums** | ✅ DONE | — | WorkflowStatus, StepType, Transition |
| **Workflow Engine** | 📋 PLANNED | 30 | Step orchestration with state machine |
| **Human Approval Gates** | 📋 PLANNED | 26 | Pause workflow for human review of destructive actions |
| **Response Playbooks** | 📋 PLANNED | 37 | Automated SIEM response workflows |
| **Graph Export** | 📋 PLANNED | 27 | Workflow visualization → Neo4j graph export |

---

## 22. Chat

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Chat ORM Model** | ✅ DONE | — | Session, message, participant models |
| **Chat Types** | ✅ DONE | — | ChatSession, ChatMessage, Participant |
| **Chat Enums** | ✅ DONE | — | MessageRole, ChatStatus, SessionType |
| **Chat Endpoints** | ✅ DONE | — | REST endpoints for message CRUD |
| **WebSocket Streaming** | 📋 PLANNED | 8+ | Real-time chat with SSE/WebSocket |
| **Memory Persistence** | 📋 PLANNED | 20 | PostgreSQL-backed chat session storage |

---

## 23. Tasks

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Task ORM Model** | ✅ DONE | 0 | TaskAssignment with payload, priority, timeout |
| **Task Types** | ✅ DONE | 0 | Task, TaskConfig, TaskResult dataclasses |
| **Task Enums** | ✅ DONE | 0 | TaskStatus, TaskPriority, TaskType |
| **Task Endpoints** | ✅ DONE | 0 | CRUD + status management REST API |
| **Task Lifecycle** | ✅ DONE | 0 | pending→assigned→running→completed/failed |
| **Team→Task Assignment** | ✅ DONE | 0 | FK to team, orchestrator isolation |

---

## 24. Marketplace

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **MarketplaceItem Registry** | ✅ DONE | 2+ | Item discovery, metadata, enable/disable |
| **Marketplace ORM Model** | ✅ DONE | 2+ | Tortoise model with item metadata |
| **Marketplace Types** | ✅ DONE | 2+ | MarketplaceItem, InstallConfig, Version |
| **Marketplace Enums** | ✅ DONE | 2+ | ItemType: tool, skill, prompt, mcp_server |
| **Marketplace Cache** | ✅ DONE | 2+ | Startup-loaded with configurable TTL |
| **Three-Ring Migration** | 📋 PLANNED | 9 | Rename registry→service.py, Registry becomes thin cache |
| **MCP Server Marketplace** | 📋 PLANNED | 22 | Install/enable MCP servers as marketplace items |

---

## 25. Prompt Registry

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Prompt Package/Enum Scaffold** | 🟡 PARTIAL RUNTIME | 23 | Package and prompt category enums exist |
| **Prompt ORM Model** | 📋 PLANNED | 23 | Versioned prompt templates with metadata |
| **Prompt Types** | 📋 PLANNED | 23 | Prompt variable, definition and render-result structs |
| **Versioned Prompt Mgmt** | 📋 PLANNED | 23 | Template CRUD + version history |
| **Agent/Team Prompt Binding** | 📋 PLANNED | 23 | Per-agent, per-team, per-session prompt resolution |
| **Prompt→Marketplace Bridge** | 📋 PLANNED | 23 | Publish prompts as marketplace items |

---

## 26. Projects

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Project ORM Model** | ✅ DONE | — | Metadata, source_dir, config |
| **Project Types** | ✅ DONE | — | ProjectConfig, ProjectMetadata |
| **Project Manager** | ✅ DONE | — | Session↔project linking |
| **Session→Project Binding** | 📋 PLANNED | 17 | ProjectManager resolves `source_dir` for session working dir |

---

## 27. LLM Proxy

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **LLM Proxy Surface** | 🟡 PARTIAL RUNTIME | 36 | `/v1/health`, `/v1/models`, and non-streaming `/v1/chat/completions` routes exist |
| **Local Proxy Service** | 🟡 PARTIAL RUNTIME | 36 | Calls module-owned `AgentExecutor`; auth, streaming, routing policy and audit remain planned |
| **Request Interception** | 📋 PLANNED | 29 | Log/audit all LLM traffic through proxy |

---

## 28. Local Assist

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Local Assist Package** | 🟡 PARTIAL RUNTIME | — | Package marker exists; typed/runtime implementation is not verified |
| **Offline Assist Capability** | 📋 PLANNED | 29 | Local AI assistant for offline operations |
| **Persistence Layer** | 📋 PLANNED | 29 | Local storage for assist data |

---

## 29. Memory Ownership Consolidation

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Canonical Memory Owner** | 🟡 PARTIAL RUNTIME | 20 | `core/memory` owns memory contracts, context window, stores and service surfaces |
| **Canonical Retrieval Owners** | 🟡 PARTIAL RUNTIME | 20 | `core/rag_vector` exists; `core/rag_graph` is the planned graph sibling |
| **Retired Parallel Branch** | ✅ REMOVED | 20 | Removed from active source/tracker planning; do not reintroduce a second persistence route |

---

## 30. RAG & Knowledgebase

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **core/rag_vector Package** | 🟡 PARTIAL RUNTIME | 20 | Models, enums, REST endpoints and keyword/hybrid retriever exist |
| **pgvector Semantic Retrieval** | 📋 PLANNED | 20 | Source currently contains an explicit actual-vector-search TODO |
| **core/rag_graph/** | 📋 PLANNED | 20 | Graph retrieval on Neo4j |
| **HybridRetrievalService** | 📋 PLANNED | 20 | Mode selection: vector | graph | hybrid | auto |
| **Result Fusion Layer** | 📋 PLANNED | 20 | Merge + rerank + dedupe + provenance preservation |
| **Retrieval Cache Layer** | 📋 PLANNED | 20 | Redis + PostgreSQL cache for query results, embedding reuse |
| **ContextAssembler** | 📋 PLANNED | 20 | Converts retrieval → provider message format |
| **CVE Feed Ingestion** | 📋 PLANNED | 20 | Vulnerability intelligence → vector store |
| **Entity Graph Projection** | 📋 PLANNED | 20 | Extracted entities → Neo4j graph for traversal |
| **Memory→RAG Bridge** | 📋 PLANNED | 20 | Session memory backed by hybrid retrieval |

---

## 31. Persistent Memory

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Memory Contracts and Types** | 🟡 PARTIAL RUNTIME | 20 | `MemoryEntry`, policy/store/retriever contracts and service surface exist |
| **Redis Hot Tier / Session Store** | 🟡 PARTIAL RUNTIME | 20 | Current session and memory runtime surfaces exist; lifecycle completion requires verification |
| **PostgreSQL Cold Tier** | 📋 PLANNED | 20 | Tortoise ORM + tsvector full-text search |
| **Context Window Assembly** | 🟡 PARTIAL RUNTIME | 20 | Context-window and agent-memory source exists; full retrieval bridge remains planned |
| **Session Lifecycle Hooks** | 📋 PLANNED | 20 | Memory init on session create, flush on end |
| **Agent Turn Hooks** | 📋 PLANNED | 20 | Read memory before turn, write after turn |

---

## 32. Triage Intelligence

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **TriageEngine** | 🟡 PARTIAL RUNTIME | 21 | Ollama-backed classification with heuristic fallback is present in `modules/triage` |
| **Triage ORM Model** | ✅ DONE | — | Classification records |
| **Triage Types** | ✅ DONE | — | TriageMetrics, ComplexityScore, RoutingDecision |
| **Triage Enums** | ✅ DONE | — | ComplexityLevel, TriageAction |
| **Public Triage API** | 🟡 PARTIAL RUNTIME | 21 | `classify_query()` and pipeline `classify()` are module-owned exports consumed by strategies/chat |
| **Qwen3-0.6B Completion** | 📋 PLANNED | 21 | Validate model selection, robustness and retained micro-features |
| **12 Micro-Features** | 📋 PLANNED | 21 | Micro-Router, Confidence Scorer, Echo Detector, Intent Drift, Tone Adapter, Parallel Micro-Voter, Token Budget Analyst, Memory Tagger, Paradox Spotter, Fallback Whisperer, Paraphrase Suggester, Pre-Filter |

---

## 33. Triage (Module)

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Triage ORM Model** | ✅ DONE | — | Classification records, routing history |
| **Triage Types** | ✅ DONE | — | TriageMetrics, ComplexityScore, RoutingDecision |
| **Triage Enums** | ✅ DONE | — | ComplexityLevel, TriageAction |

---

## 34. Strategies

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Strategies Module** | 🟡 PARTIAL RUNTIME | 8/21 | Pipeline, router and strategy implementations exist |
| **Response Strategy Router** | 🟡 PARTIAL RUNTIME | 21 | Calls the public triage API and maps complexity to injection strategy |
| **Strategy Implementations** | 🟡 PARTIAL RUNTIME | 8 | Direct, prepend/chain, balanced, cost and latency surfaces exist |
| **Provider Routing Boundary** | 📋 PLANNED | 13 | Do not confuse response strategies with budget/circuit-breaker provider routing |

---

## 35. Human Approval Workflows

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Approval Gates** | 📋 PLANNED | 26 | Pause destructive-action workflows for human review |
| **Approval Request API** | 📋 PLANNED | 26 | REST endpoints for pending approval list + approve/reject |
| **SIEM Destructive Action Guard** | 📋 PLANNED | 37 | Approval required before executing response playbooks |

---

## 36. CQRS Event Store

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **DomainEvent Struct** | 📋 PLANNED | 6 | Immutable msgspec.Struct: event_type, aggregate_id, payload, correlation_id |
| **EventStore (PostgreSQL)** | 📋 PLANNED | 6 | Append-only DomainEventRecord table with replay capability |
| **Redis Stream Fan-Out** | 📋 PLANNED | 6 | XADD to `css:events` for multi-consumer distribution |
| **CommandBus** | 📋 PLANNED | 6 | Command + handler pattern for domain mutations |
| **Read Projections** | 📋 PLANNED | 6 | PermissionProjection, AuditProjection rebuilt from event stream |
| **OtelBridge** | 📋 PLANNED | 6 | DomainEvent → OTEL span → OpenObserve |
| **@instrument Decorator** | 📋 PLANNED | 14 | Auto-emit DomainEvents at entry/exit of any async function |
| **FastAPI Middleware** | 📋 PLANNED | 14 | HTTP request instrumentation with W3C traceparent extraction |

---

## 37. Observability & Monitoring

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **OpenObserve Integration** | ✅ DONE | — | Docker service at :5080, Dashboards, traces, metrics, structured logs |
| **OpenTelemetry Config Surface** | 🟡 PARTIAL RUNTIME | 35 | `core/otel/config.py` and package export exist; instrumentation/data-plane implementation remains |
| **OTEL Auto-Instrumentation** | 📋 PLANNED | 14 | fastapi + aiohttp zero-code instrumentation |
| **OtelBridge Service** | 📋 PLANNED | 6 | DomainEvent stream → OTEL spans → OpenObserve |
| **Event Timeline Dashboard** | 📋 PLANNED | 35 | OpenObserve dashboard for event stream visualization |
| **Cost Telemetry** | 📋 PLANNED | 35 | Per-provider cost tracking emitted to OpenObserve |
| **Cache Hit/Miss Metrics** | 📋 PLANNED | 11 | `cache.hit`/`miss`/`native` events emitted to OpenObserve |
| **QoL Injection Metrics** | 📋 PLANNED | 12 | `qol.injection` events in OpenObserve |

---

## 38. Permissions & Security

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Permissions Module Structure** | 🟡 PARTIAL RUNTIME | 15 | Structures/checker surface exists; source TODO confirms tool permission enforcement is incomplete |
| **PathGrant / ToolGrant** | 📋 PLANNED | 15 | File-path and tool-call permission grants |
| **PermissionChecker** | 📋 PLANNED | 15 | Enforce grants at session entry and tool execution |
| **Session Isolation** | 📋 PLANNED | 15 | `~/.css/sessions/` directory permissions |
| **RBAC Access Control** | 📋 PLANNED | 28 | Role-based access for multi-user platform |
| **Auth Module** | 🟡 PARTIAL RUNTIME | 28 | JWT/API-key/password manager and routes exist; credential/auth checks remain TODO-marked |
| **Accounts Module** | 🟡 PARTIAL RUNTIME | 28 | Accounts endpoints exist; integration and isolation remain planned |
| **API Key Management** | 🟡 PARTIAL RUNTIME | 28 | Route/manager surfaces exist; caller authorization remains incomplete |
| **Secrets Redaction** | 📋 PLANNED | 12 | QoL toggle: auto-redact API keys/passwords/tokens in output |

---

## 39. Graph Visualization

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Graph Visualization Engine** | 📋 PLANNED | 27 | Render Neo4j graphs in frontend |
| **XYFlow Integration Baseline** | 📋 PLANNED | 18/27 | Standard graph/canvas UI engine for frontend topology and graph views |
| **Attack-Path Traversal** | 📋 PLANNED | 27 | Visualize MITRE ATT&CK technique chains |
| **Workflow Graph Export** | 📋 PLANNED | 27 | Workflow steps → Neo4j graph → visualization |

---

## 40. Git & Version Control

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Git Tracking** | 📋 PLANNED | 24 | Track project state across session boundaries |
| **Worktree Isolation** | 📋 PLANNED | 24 | Per-session git worktree for safe parallel modifications |

---

## 41. Frontend

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Vite + React 19 Shell** | 🟡 PARTIAL RUNTIME | 18 | Frontend package, Tailwind/shadcn components and router source exist |
| **Module-Colocated Panels** | 🟡 PARTIAL RUNTIME | 18 | Marketplace panel/template surfaces exist; broader migration remains |
| **AppShell / Sidebar** | ✅ DONE | 18 | `AppShell`, `Sidebar`, `TopBar`, `PanelContainer` present in source |
| **API Client** | 🟡 PARTIAL RUNTIME | 18 | `src/frontend/src/core/api/client.ts` exists; feature coverage requires validation |
| **WebSocket Manager** | 📋 PLANNED | 18 | Singleton, typed subscribe, reconnection |
| **SSE Client** | 📋 PLANNED | 18 | AsyncGenerator over HTTP SSE |
| **ECharts + Worker Graphs** | 📋 PLANNED | 18/27 | Retained replacement for the prior Recharts proposal |
| **Landing Dashboard** | 🟡 PARTIAL RUNTIME | 18 | `LandingDashboard.tsx` exists; live metrics wiring remains planned |
| **Frontend Tracker Status** | 🟡 PARTIAL RUNTIME | 18 | 8 done / 35 pending in `.plan/session.db` |

---

## 42. Core Infrastructure

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **ASGI Module** | 🟡 PARTIAL RUNTIME | 36 | FastAPI lifespan/router/process surfaces exist; mounted transport policy remains pending |
| **DB Module** | 🟡 PARTIAL RUNTIME | 40 | Tortoise/PostgreSQL source exists; remaining model consolidation work resumes after Phase 41 preparation |
| **Types Module** | ✅ DONE | — | 1654 LOC, 13 root files + 5 provider files (oversized, needs refactor) |
| **Config System** | 🟡 PARTIAL RUNTIME | 17 | Current core/config source has a migration TODO toward canonical settings/config ownership |
| **Module Auto-Discovery** | ✅ DONE | 2 | Dynamic module scanning via importlib |
| **Orchestration Roles** | ✅ DONE | 2 | Orchestrator/TeamLeader/TeamMember role system |
| **Cache System** | ✅ DONE | — | core/cache with Redis backend |
| **Loader** | ✅ DONE | — | Module loading, router registration |
| **Docker Infrastructure** | ✅ DONE | — | PostgreSQL + Redis + Neo4j + OpenObserve |
| **Types Subdirectory Refactor** | 📋 PLANNED | 4 | Consolidate into base/, api/, events/, providers/ subdirs |
| **entry_points Plugin System** | 📋 PLANNED | 6 | Replace pkgutil with importlib.metadata, 20-line loader |
| **msgspec.Struct Migration** | 📋 PLANNED | 6, 9 | Replace @dataclass with msgspec.Struct (10-40× faster serde) |
| **Three-Ring Architecture** | 📋 PLANNED | 9 | Value Types → ORM Models → In-Memory Registries |
| **Tortoise Custom Managers** | 📋 PLANNED | 9 | Replace scattered `.filter()` with typed Manager methods |
| **Service Layer** | 📋 PLANNED | 9 | `service.py` per module — only entry point for business logic |
| **Core Root Ownership** | ✅ CLEANED | — | Module-owned triage/routing facades removed; consumers import canonical module APIs |

---

## 43. API Provider SDKs (24 Providers)

| Provider | Status | Notes |
|----------|--------|-------|
| **Anthropic** | ✅ DONE | Reference impl: prompt_caching, computer_use, extended_thinking |
| **OpenAI** | ✅ DONE | Optional native adapter + OpenAI-compat template |
| **Gemini** | ✅ DONE | Proprietary API, cachedContent resource |
| **Groq** | ✅ DONE | OpenAI-compatible, fast inference |
| **Mistral** | ✅ DONE | Proprietary, chat + rerank endpoints |
| **Ollama** | ✅ DONE | Local, `/api/chat`, model management |
| **OpenRouter** | ✅ DONE | Proxy pattern, multi-model routing |
| **Cohere** | ✅ DONE | Reranking + embedding specialized |
| **AI21** | ✅ DONE | Research-focused, batch support |
| **Together** | ✅ DONE | Open-source model hosting |
| **GitHub Copilot** | ✅ DONE | Mixed cloud/local, agentic workflows |
| **DeepInfra** | ✅ DONE | OpenAI-compatible, multi-model |
| **Cerebras** | ⏳ PENDING | Wafer-scale hardware, proprietary API |
| **Cloudflare** | ⏳ PENDING | Workers AI or separate service |
| **DeepSeek** | ⏳ PENDING | OpenAI-compatible, popular |
| **Fireworks** | ⏳ PENDING | OpenAI-compatible, undocumented |
| **HuggingFace** | ⏳ PENDING | Missing plan.md, needs initial research |
| **LambdaAPI** | ⏳ PENDING | Scope unclear |
| **NScale** | ⏳ PENDING | Early stage, minimal public info |
| **NVIDIA** | ⏳ PENDING | GPU cloud API |
| **OpenCode** | ⏳ PENDING | Code-specific or general LLM |
| **Perplexity** | ⏳ PENDING | Search + conversational, proprietary |
| **SambaNova** | ⏳ PENDING | RDU hardware, specialized rate limits |
| **XAI** | ⏳ PENDING | Grok access, OpenAI-compatible |

---

## 44. Planned and Scaffolded Modules

| Module | Source state | Phase | Description |
|--------|--------------|-------|-------------|
| **Auth** | 🟡 Partial runtime | 28 | JWT/API-key manager and route scaffold; authorization TODOs remain |
| **Accounts** | 🟡 Partial runtime | 28 | Account route/model surfaces; isolation completion pending |
| **Approvals** | Documentation owner only | 26 | Human approval gates for destructive actions |
| **Notifications** | Planned | 25 | Event-driven notification dispatcher |
| **Graphs** | Documentation owner only | 27 | Graph visualization engine |
| **Sessions** | Package/document scaffold | 19 | Session lifecycle management |

---

## 45. IDE PyCharm Integration

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Typed IDE Surface** | 🟡 PARTIAL RUNTIME | 38 | Types/enums/exceptions and placeholder clients/endpoints exist |
| **Real Connector Invocation** | 📋 PLANNED | 38 | Client placeholders must call real IDE connector capabilities |
| **Agent Wiring** | 📋 PLANNED | 38 | Sole pending tracked Phase 38 todo |

---

## 46. DB Model Consolidation

| Feature | Status | Phase | Description |
|---------|--------|-------|-------------|
| **Marketplace Model Lane** | 🟡 PARTIAL RUNTIME | 40 | `db40-lane-marketplace` is done in the tracker; remaining Phase 40 work resumes after the Phase 41 preparation gate |
| **Menu/Tree Contract** | 🟡 PARTIAL RUNTIME | 40 | `menu.py` and menu-id contract exist; validate completed lane behavior against source/tests |
| **Direct Development Schema Policy** | ✅ RETAINED | 40 | Production migration/versioning remains a later explicit decision |

---

## Phase Completion Summary

Queried from `.plan/session.db` on 2026-05-26. Phase 40 is positioned
before Phase 9 by the current execution order.

| Phase | Title | Total | Done | Pending | Blocked | Active |
|------:|-------|------:|-----:|--------:|--------:|-------:|
| 0 | TeamScope Foundation | 12 | 12 | 0 | 0 | 0 |
| 1 | Multi-Orchestrator Core | 16 | 16 | 0 | 0 | 0 |
| 2 | SDK Architecture | 64 | 64 | 0 | 0 | 0 |
| 3 | Module Consistency | 155 | 153 | 0 | 2 | 0 |
| 4 | Core Consistency + Types | 24 | 22 | 0 | 2 | 0 |
| 5 | Integration & Testing | 32 | 32 | 0 | 0 | 0 |
| 6 | Architecture Overhaul | 37 | 37 | 0 | 0 | 0 |
| 7 | Feature Completeness | 19 | 19 | 0 | 0 | 0 |
| 8 | AI Execution Layer | 17 | 17 | 0 | 0 | 0 |
| 40 | DB Model Consolidation & Rich Schemas | 37 | 7 | 30 | 0 | 0 |
| 9 | ORM / Manager / Registry | 32 | 32 | 0 | 0 | 0 |
| 10 | Unified SDK Architecture | 16 | 11 | 5 | 0 | 0 |
| 11 | Cross-Provider Prompt Caching | 10 | 0 | 9 | 1 | 0 |
| 12 | QoL Output Controls Migration | 11 | 1 | 10 | 0 | 0 |
| 13 | Provider Routing & Resilience | 15 | 0 | 15 | 0 | 0 |
| 14 | Event Hooks & Instrumentation | 18 | 8 | 10 | 0 | 0 |
| 15 | Permissions + WorkingDir | 31 | 0 | 31 | 0 | 0 |
| 16 | Provider SDK Features | 31 | 0 | 31 | 0 | 0 |
| 17 | Settings & Projects | 39 | 0 | 39 | 0 | 0 |
| 18 | Frontend Foundation | 43 | 8 | 35 | 0 | 0 |
| 19 | Module Restructuring + Sessions | 15 | 3 | 11 | 1 | 0 |
| 20 | Persistent Memory Layer | 43 | 7 | 36 | 0 | 0 |
| 21 | Qwen3-0.6B Triage Intelligence | 15 | 0 | 15 | 0 | 0 |
| 22 | MCP Protocol Layer | 8 | 5 | 3 | 0 | 0 |
| 23 | Prompt Registry | 11 | 1 | 10 | 0 | 0 |
| 24 | Git Tracking & Worktree Isolation | 9 | 0 | 9 | 0 | 0 |
| 25 | Integration Hardening | 14 | 8 | 6 | 0 | 0 |
| 26 | Human Approval Workflows | 14 | 0 | 14 | 0 | 0 |
| 27 | Graph Visualization Engine | 17 | 0 | 17 | 0 | 0 |
| 28 | Auth & Accounts | 6 | 1 | 5 | 0 | 0 |
| 29 | Cybersec Domain Layer | 10 | 0 | 10 | 0 | 0 |
| 30 | Workflow Engine + IPC | 5 | 0 | 5 | 0 | 0 |
| 31 | Production Readiness | 7 | 0 | 7 | 0 | 0 |
| 32 | Reports Module | 11 | 0 | 11 | 0 | 0 |
| 33 | Ollama Native | 6 | 0 | 6 | 0 | 0 |
| 34 | Dependency Map | 20 | 2 | 18 | 0 | 0 |
| 35 | Telemetry Infrastructure | 7 | 0 | 7 | 0 | 0 |
| 36 | Local Proxy & Transport Surfaces | 8 | 2 | 6 | 0 | 0 |
| 37 | SIEM/EDR Integration | 6 | 0 | 6 | 0 | 0 |
| 38 | IDE PyCharm | 5 | 4 | 1 | 0 | 0 |
| 39 | Audit Remediation (A1/A2/A3) | 19 | 1 | 18 | 0 | 0 |
| 41 | Plan Quality Remediation | 12 | 12 | 0 | 0 | 0 |

**Overall**: 927 total / 485 done / 436 pending / 6 blocked / 0 in progress.
Phase 41 preparation is complete; later implementation must resume through a
dependency-ready tracker row and its verified owner specification.
