# CyberSecSuite Architecture

**Status**: 🏗️ Detailed System Design  
**Updated**: 2026-05-03  
**Scope**: Multi-Orchestrator + TeamScope implementation

---

## 📐 SYSTEM OVERVIEW

### Execution Model: Main Processes by Mode

Sessions spawn different numbers of main orchestrator processes depending on mode:

#### Development Mode (3 Main Processes)
```
Session [mode=development]

Process 1: Planner Orchestrator
├─ Role: Planning & decision making
├─ Access: Read-only project code
├─ Output: Proposals, decisions (to .css/plan/)
├─ Model: LLM (for planning)
└─ Capability: Delegate to planning teams

Process 2: Normal Orchestrator (Main)
├─ Role: Primary execution
├─ Access: Full project scope (read/write)
├─ Output: Code changes, results
├─ Model: LLM (for implementation)
└─ Capability: Execute tasks, create teams, spawn subprocesses

Process 3: Background Orchestrator (Triage)
├─ Model: Qwen3-0.6B (lightweight, always-on)
├─ Role: Task triage & routing
├─ Access: Read project, limited write (logs)
└─ Capability: Route tasks to appropriate teams/processes
```

#### Other Modes: Red/Blue/Purple (2 Main Processes)
```
Session [mode=red_team|blue_team|purple_team]

Process 1: Normal Orchestrator (Main)
├─ Role: Attack/Defense/Coordinated execution
├─ Access: Full project scope (read/write)
├─ Output: Findings, results, mitigations
├─ Model: LLM (for simulation)
└─ Capability: Execute tasks, create teams, spawn subprocesses

Process 2: Background Orchestrator (Triage)
├─ Model: Qwen3-0.6B (lightweight, always-on)
├─ Role: Task triage & routing
├─ Access: Read project, limited write (logs)
└─ Capability: Route tasks to appropriate teams/processes
```

### Main Orchestrator Capabilities

Each main orchestrator (in any process) has:

```
Main Orchestrator
├─ Access: Full Project Scope ($(pwd)/)
├─ Can execute inline async tasks (in same process)
└─ Can delegate to Teams/Roles (spawn subprocess)
   ├─ Team runs in isolated subprocess
   ├─ Team has own PID, memory, event loop
   ├─ Team contains TeamLeader + roles
   ├─ Team must report results back via IPC
   └─ Communication: Pipe or socket
```

### Scope Hierarchy (Corrected)

```
AppScope
  ↓
ProjectScope
  ↓
┌────────────────────┬─────────────────┐
│  SessionScope      │  PlanScope      │
│  (sibling scopes)  │  (dev mode only)│
├────────────────────┼─────────────────┤
│ WorkDir:           │ WorkDir:        │
│ .css/sessions/     │ .css/plan/      │
│ session-<sid>/     │                 │
│                    │ Main Orch       │
│ Creates:           │ (Planner only)  │
│ • Teams            │ Read: project   │
│ • Tasks            │ Write: .css/    │
│ • Async procs      │ plan/           │
│ • Processes        │                 │
│                    │ Permissions:    │
│ ├─ TeamScope       │ Read .plan/,    │
│ │  WorkDir:        │ Write .css/     │
│ │  .css/teams/     │ plan/ only      │
│ │  team-<id>/      │                 │
│ │  • TeamLeader    │                 │
│ │  • Roles (with   │                 │
│ │    Permissions:  │                 │
│ │    R/W team-<id>/│                 │
│ │    only)         │                 │
│ │                  │                 │
│ └─ OrchestratorPool│                 │
│    (per team)      │                 │
│                    │                 │
└────────────────────┴─────────────────┘
```

### Result
- **Before**: Serial execution, 1 task at a time
- **After**: N tasks in parallel, organized by teams, fault-isolated

---

## 🎭 ROLE ABSTRACTION LAYER

### Concept: Unified Capability Stack

**Role** is the top-level abstraction that unifies all capability types:

```
┌─────────────────────────────────────────┐
│           ROLE (Persona/Skill)          │
│  (Unified abstraction layer)            │
└─────────────────────────────────────────┘
                    ↓
    ┌───────────────┬───────────────┬─────────────┐
    ↓               ↓               ↓             ↓
┌─────────┐   ┌─────────┐   ┌──────────┐   ┌──────────┐
│ AGENTS  │   │ SKILLS  │   │ TOOLS    │   │ MCPs &   │
│ (LLM)   │   │ (Data)  │   │ (Direct) │   │ SDKs     │
└─────────┘   └─────────┘   └──────────┘   └──────────┘
```

### Stack Details

1. **Agents** (LLM-powered)
   - 18 deployed specialist agents (cybersec-agent, code-reviewer, etc.)
   - Invoke via orchestrator + Claude Agent SDK
   - Streaming support, tool/MCP integration

2. **Skills** (Data/Knowledge)
   - Marketplace skills (installable bundles)
   - Agent-attached skill libraries
   - SKILL.md metadata (model, tools, max_turns, domain, tags)

3. **Tools** (Direct Callables)
   - 87 registered MCP tools (findings, IOCs, cache, AI proxy, etc.)
   - Direct function calls (no LLM invocation needed)
   - Synchronous or async execution

4. **MCPs & SDKs** (External Integrations)
   - 7 bootstrap MCPs (csscore, canvas, memory, template, playwright, crypto, custom)
   - Provider SDKs (Anthropic, OpenAI, Groq, etc.)
   - Direct SDK calls for specialized work

### Role Encapsulates All 4 Layers

A **Role** definition:
```python
@dataclass
class Role:
    """Role = unified capability across agents, skills, tools, MCPs"""
    role_id: str           # e.g., "senior-engineer"
    agents: List[Agent]    # Which agents can this role spawn?
    skills: List[Skill]    # Which skills are attached?
    tools: List[Tool]      # Which tools can it call?
    sdk_access: Dict       # Which MCPs/SDKs are available?
    max_concurrent: int    # Parallelism limit
    timeout_sec: int       # Execution timeout
```

### Use Case: Orchestrator → Role → Capabilities

```
Orchestrator
├─ "Create security analysis"
│  └─ SELECT role='security-analyst'
│     ├─ Agents: [reverse-engineer, logfile-analyst]
│     ├─ Skills: [binary-analysis, log-parsing]
│     ├─ Tools: [query_iocs, suggest_mitre]
│     └─ MCPs: [dystopian-crypto, opensearch]
│
└─ "Build new feature"
   └─ SELECT role='senior-engineer'
      ├─ Agents: [code-reviewer, python-developer]
      ├─ Skills: [testing, fastapi, tortoise-orm]
      ├─ Tools: [cache_lookup, cache_store]
      └─ MCPs: [playwright, custom-mcp]
```

### Benefits
- ✅ Single entry point (Role) instead of juggling agents/skills/tools
- ✅ Composable: combine any agents, skills, tools in a role
- ✅ Permission model: role grants access to specific capabilities
- ✅ Scalable: can create unlimited role combinations
- ✅ Template-based: marketplace roles (pre-configured combinations)

---

### Two Hierarchies: Scope + Process

#### Hierarchy 1: SCOPE (Filesystem & Configuration)

```
Level 1: Global Scope (~/.css/)
         ├─ User config, credentials, cache
         ├─ Cross-project settings
         └─ Read/Write access

         ↓ (Config cascade)

Level 2: Project Scope ($(pwd)/)
         ├─ Full project directory
         ├─ Source code (/src)
         ├─ Project config ($(pwd)/.css/)
         ├─ Sessions container ($(pwd)/.css/sessions/)
         └─ Full read/write access (all processes)

         ↓ (Config cascade)

Level 3: Session Scope ($(pwd)/.css/sessions/session-<sid>/)
         ├─ Session metadata & config (overrides project)
         ├─ Teams container (if multi-team mode)
         ├─ Task queues & results
         └─ Session-specific read/write access

         ↓ (Organization)

Level 4: TeamScope ($(pwd)/.css/sessions/session-<sid>/teams/team-<tid>/)
         ├─ Team metadata & config
         ├─ Team task queue (isolated from other teams)
         ├─ Team results (isolated)
         ├─ Team artifacts
         └─ Team-isolated read/write access
```

**Config Cascade** (highest → lowest priority):
1. Session Scope: `$(pwd)/.css/sessions/session-<sid>/config.yaml`
2. Project Scope: `$(pwd)/.css/config.yaml`
3. Global Scope: `~/.css/config.yaml`
4. Built-in defaults

---

#### Hierarchy 2: PROCESS (Execution Model)

```
Orchestrator Hierarchy (Mode-Dependent)

DEVELOPMENT MODE (3 Main Processes)
│
├─ Process 1: Planner Orchestrator
│  ├─ Role: Planning & decision making
│  ├─ Access: Read-only project scope, write to plan/ only
│  ├─ Capability: Can delegate to planning teams
│  └─ Output: Proposals, decisions (to plan/)
│
├─ Process 2: Normal Orchestrator (Main)
│  ├─ Role: Primary execution
│  ├─ Access: Full project scope (read/write)
│  ├─ Capability: Execute tasks, create teams, spawn orchestrators
│  └─ Output: Code changes, results
│
└─ Process 3: Background Orchestrator (Triage/Routing)
   ├─ Model: Qwen3-0.6B (lightweight, always-on)
   ├─ Role: Background task triage & routing
   ├─ Access: Read project scope, limited write (logs)
   ├─ Capability: Route tasks to appropriate teams/processes
   └─ Output: Task routing decisions


OTHER MODES (Red/Blue/Purple) (2 Main Processes)
│
├─ Process 1: Normal Orchestrator (Main)
│  ├─ Role: Primary execution (attack/defense/both)
│  ├─ Access: Full project scope (read/write)
│  ├─ Capability: Execute tasks, create teams, spawn orchestrators
│  └─ Output: Results, findings, mitigations
│
└─ Process 2: Background Orchestrator (Triage/Routing)
   ├─ Model: Qwen3-0.6B (lightweight, always-on)
   ├─ Role: Background task triage & routing
   ├─ Access: Read project scope, limited write (logs)
   ├─ Capability: Route tasks to appropriate teams/processes
   └─ Output: Task routing decisions


PROCESS INTERACTION PATTERN
│
Main Orchestrator (any of above)
│
├─ [Async Tasks]
│  └─ Run inline in same process
│     └─ Full project scope access
│
└─ [Delegated Teams/Roles]
   └─ Spawn subprocess (isolated context)
      ├─ Subprocess has:
      │  ├─ Own PID
      │  ├─ Own memory space
      │  ├─ Own event loop (asyncio)
      │  └─ Own working directory
      │
      ├─ Team Leader (runs in subprocess)
      │  ├─ Manages team roles
      │  ├─ Receives delegations from parent
      │  ├─ Reports results back
      │  └─ Monitors subprocess health
      │
      └─ [Communication Channel]
         ├─ Pipe or socket
         ├─ Bidirectional (parent ↔ child)
         └─ Reports must include callback_id for correlation
```

**Key Points**:
- **Scope Hierarchy**: Filesystem + config organization (global → project → session → team)
- **Process Hierarchy**: Execution organization (main processes + delegated subprocesses)
- **Each Main Orchestrator**: Has full Project Scope access
- **Delegated Teams**: Run in subprocess with isolated context, must report back
- **Communication**: Parent-child IPC (pipe/socket) for delegation & results

### Scope Resolution (Config Cascade)
**Priority Order** (highest → lowest):
1. Session Scope (`$(pwd)/.css/sessions/session-<sid>/config.yaml`)
2. Project Scope (`$(pwd)/.css/config.yaml`)
3. Global Scope (`~/.css/config.yaml`)
4. Built-in defaults

Each level can override values from lower levels.

### Session Run Mode Config
```yaml
# Global config in ~/.css/config.yaml
global:
  credentials_path: ~/.css/credentials/
  cache_dir: ~/.css/cache/

# Project config in $(pwd)/.css/config.yaml
project:
  session_mode: development  # development | red_team | blue_team | purple_team
  max_sessions: 10
  enable_background_triage: true

# Session config in $(pwd)/.css/sessions/session-<sid>/config.yaml
session:
  run_mode: development      # development | red_team | blue_team | purple_team
  enable_background_triage: true
  background_model: "qwen3-0.6B"
```

---

## 🗂️ FILESYSTEM LAYOUT

### Global Scope
```
~/.css/
├── config.yaml              # Global user config
├── credentials/
│   ├── openai.key
│   ├── anthropic.key
│   └── groq.key
├── cache/                   # Global cache
│   ├── embeddings/
│   └── models/
└── logs/                    # User-level logs
    └── app.log
```

### Project Scope
```
$(pwd)/.css/
├── config.yaml              # Project config (overrides global)
├── state/                   # Project state files
│   └── metadata.json
├── sessions/                # Session container
│   ├── session-abc123/      # Actual sessions
│   ├── session-def456/
│   └── session-ghi789/
├── artifacts/               # Project-level artifacts
└── logs/                    # Project logs
    └── app.log
```

### Session Scope
```
$(pwd)/.css/sessions/session-<sid>/
├── config.yaml              # Session config (includes run_mode)
├── metadata.json            # Session info (id, created_at, run_mode, etc.)
├── plan/                    # PLAN ORCHESTRATOR OUTPUT (development mode only)
│   ├── decisions/           # Planning decisions, proposals
│   ├── analysis/            # Architecture analysis
│   ├── proposals.md         # Feature proposals
│   └── logs/
│
├── teams/                   # Team subdivisions
│   ├── team-eng/
│   │   ├── config.yaml      # Team-specific config
│   │   ├── queue.db         # SQLite queue (team tasks)
│   │   ├── orchestrators/   # Team orchestrator state
│   │   │   ├── orch-1.json
│   │   │   ├── orch-2.json
│   │   │   └── orch-3.json
│   │   ├── results/         # Team-specific results
│   │   └── logs/
│   │
│   ├── team-security/
│   │   ├── config.yaml
│   │   ├── queue.db
│   │   ├── orchestrators/
│   │   ├── results/
│   │   └── logs/
│   │
│   └── team-compliance/
│       └── [similar structure]
│
├── orchestrators/           # If no teams (legacy)
├── tasks/                   # Task definitions & status
│   ├── task-001.json
│   └── task-002.json
├── results/                 # Aggregated results
│   └── results.json
└── logs/                    # Session logs
    └── app.log
```

---

## 🏗️ PYTHON PROJECT STRUCTURE (Django-like)

```
src/css/
│
├── core/                    # Shared Infrastructure
│   ├── db/
│   │   ├── models/          # ORM models (Tortoise)
│   │   │   ├── scope.py     # ProjectScope, AppScope, SessionScope, TeamScope
│   │   │   ├── orchestrator.py  # OrchestratorInstance model
│   │   │   ├── task.py      # Task, TaskAssignment models
│   │   │   └── __init__.py
│   │   ├── migrations/      # Alembic migrations
│   │   └── __init__.py
│   │
│   ├── types/               # Shared type definitions
│   │   ├── scope.py         # ScopeType, ScopeLevel enums
│   │   ├── task.py          # TaskStatus, TaskType enums
│   │   ├── team.py          # Team types
│   │   └── __init__.py
│   │
│   ├── exceptions/          # Custom exceptions
│   │   ├── scope.py         # ScopeNotFound, ScopeError
│   │   ├── orchestrator.py  # OrchestratorError, CrashDetected
│   │   ├── task.py          # TaskError, AllocationError
│   │   └── __init__.py
│   │
│   ├── utils/               # Utility functions
│   │   ├── async_helpers.py # async context managers, utilities
│   │   ├── config.py        # Config loading, resolution
│   │   ├── filesystem.py    # Path building, scope paths
│   │   └── __init__.py
│   │
│   ├── middleware/          # Request/response middleware
│   │   └── __init__.py
│   │
│   ├── decorators/          # Common decorators
│   │   ├── async_retry.py   # Async retry logic
│   │   ├── metrics.py       # Performance tracking
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── api_services/            # LLM API Integrations
│   ├── base.py              # Abstract APIAdapter interface
│   ├── openai/
│   │   ├── adapter.py       # OpenAI implementation
│   │   └── __init__.py
│   ├── anthropic/
│   │   ├── adapter.py       # Claude implementation
│   │   └── __init__.py
│   ├── groq/
│   │   ├── adapter.py       # Groq implementation
│   │   └── __init__.py
│   └── __init__.py
│
├── modules/                 # Feature Modules (Nicely Separated)
│   │
│   ├── orchestrator/        # Orchestrator Core
│   │   ├── core.py          # OrchestratorInstance main logic
│   │   ├── queue.py         # Task queue (pull-based)
│   │   ├── monitor.py       # Heartbeat, crash detection
│   │   ├── tasks.py         # Task execution
│   │   ├── result_merge.py  # Atomic result merging, idempotency
│   │   ├── team_leader.py   # Team leader communication protocol
│   │   ├── agent_loader.py  # Agent hotloading mechanism
│   │   ├── delegator.py     # Agent delegation (async/sync)
│   │   └── __init__.py
│   │
│   ├── team_scope/          # TeamScope Logic
│   │   ├── models.py        # Team entity, dataclass
│   │   ├── manager.py       # Team CRUD, lifecycle
│   │   ├── queue.py         # Team-specific task queue
│   │   ├── metrics.py       # Team metrics, monitoring
│   │   ├── context_isolation.py  # Process-level isolation
│   │   └── __init__.py
│   │
│   ├── forensics/           # Forensic Analysis
│   │   ├── analyzer.py
│   │   ├── reporter.py
│   │   └── __init__.py
│   │
│   ├── reporting/           # Report Generation
│   │   ├── generator.py
│   │   └── __init__.py
│   │
│   ├── agents/              # Agent Implementations (Hotloadable)
│   │   ├── base_agent.py    # Abstract base
│   │   ├── forensic_agent.py
│   │   ├── registry.py      # Agent registry (for hotloading)
│   │   ├── loader.py        # Dynamic import/hotload agents
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── config.py                # Configuration Management
│   ├── load_config()        # Load + cascade (global → project → session)
│   ├── ConfigManager class  # Centralized config access
│   └── Env variables, defaults
│
├── manager.py               # Application Factory & Manager
│   ├── ApplicationManager class
│   ├── initialize()         # Setup async loop, DB, services
│   ├── create_session()     # Create forensic session
│   ├── create_team()        # Create team within session
│   ├── spawn_orchestrator() # Spawn new orchestrator
│   └── shutdown()           # Graceful cleanup
│
└── __init__.py
```

### Architecture Principles
- **Separation of Concerns**: Each module handles one responsibility
- **DRY**: Shared logic in `core/`, reused by modules
- **Factory Pattern**: `manager.py` handles initialization and creation
- **API Abstraction**: `api_services/base.py` defines adapter interface
- **Type Safety**: Tortoise ORM models + Pydantic validators
- **Async-Native**: 100% async code, no blocking I/O, no sync functions

---

## 🔄 FEATURE 1: MULTI-ORCHESTRATOR ARCHITECTURE

### Problem → Solution
```
PROBLEM:  1 orchestrator per session → Serial execution (slow)
SOLUTION: N orchestrators per session → Parallel execution (fast)
```

### Task Queue Pattern (Pull-Based)
```
Database (PostgreSQL)
│
├─ Task Queue Table
│  ├─ task_1 (pending)
│  ├─ task_2 (pending)
│  ├─ task_3 (pending)
│  ├─ task_4 (pending)
│  └─ task_5 (pending)
│
└─ Orchestrator Instances (independent agents)
   │
   ├─ Orchestrator-1
   │  ├─ [Loop]
   │  │  ├─ Check heartbeat
   │  │  ├─ Pull next task from queue (atomic)
   │  │  ├─ Execute task
   │  │  └─ Push result to result_queue
   │  └─ [Repeat]
   │
   ├─ Orchestrator-2
   │  ├─ [Same independent loop]
   │  └─ [Repeat]
   │
   └─ Orchestrator-3
      ├─ [Same independent loop]
      └─ [Repeat]

Result: All 5 tasks executed in parallel, independent processes
```

### Orchestrator Lifecycle
```
1. SPAWN
   ├─ Create orchestrator record in DB
   ├─ Assign UUID, session_id, team_id
   ├─ Start process (subprocess or container)
   ├─ Set status = "active"
   └─ Start heartbeat

2. RUNNING
   ├─ Pull task from queue
   ├─ Execute (async)
   ├─ Push result + idempotency_key
   ├─ Update heartbeat every 5s
   ├─ Repeat

3. CRASH DETECTION
   ├─ Monitor: heartbeat_at < now() - 300s
   ├─ Set status = "crashed"
   ├─ Reassign tasks: assigned_to=orch_id → pending
   ├─ Alert team/session

4. RECOVERY
   ├─ Spawn replacement orchestrator
   ├─ Old tasks become pending (pullable by new orch)
   ├─ Idempotency keys prevent re-execution

5. SHUTDOWN (Graceful)
   ├─ Set status = "shutting_down"
   ├─ Wait for current task to complete
   ├─ Push final result
   ├─ Set status = "inactive"
   └─ Clean up resources
```

---

## 🎭 FEATURE 2: TEAMSCOPE ARCHITECTURE

### Problem → Solution
```
PROBLEM:  All tasks in single queue → Monolithic, no isolation
SOLUTION: Teams with separate queues → Complete isolation
```

### TeamScope Hierarchy
```
SessionScope
│
├─ Team-1: Engineering (max 3 orch)
│  ├─ Team-specific config
│  ├─ Isolated task queue
│  ├─ Orchestrator-1, -2, -3 (independent)
│  ├─ Results (team-isolated)
│  └─ Resource quota: 3 concurrent orchestrators
│
├─ Team-2: Security (max 10 orch)
│  ├─ Team-specific config
│  ├─ Isolated task queue (separate DB)
│  ├─ Orchestrator-1 through -10 (independent)
│  ├─ Results (team-isolated)
│  └─ Resource quota: 10 concurrent orchestrators
│
└─ Team-3: Compliance (max 1 orch)
   ├─ Team-specific config
   ├─ Isolated task queue
   ├─ Orchestrator-1 (single)
   ├─ Results (team-isolated)
   └─ Resource quota: 1 concurrent orchestrator

ISOLATION BENEFITS:
✅ Team-1 crash → Teams 2 & 3 unaffected
✅ Team-1 exceeds quota → Teams 2 & 3 continue
✅ Team-1 paused → Teams 2 & 3 run normally
✅ Resource contention eliminated (static quotas)
```

### Team Data Model
```python
@dataclass
class Team:
    id: int
    session_id: int
    name: str                          # "engineering", "security", etc.
    team_type: str = "general"
    max_concurrent_orchestrators: int = 3  # Resource quota
    orchestrator_timeout_sec: int = 300
    orchestrator_count: int = 0        # Current count
    status: str = "active"             # active | paused | completed
    priority: int = 1                  # 1-10 (higher = more resources)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
```

### Team Lifecycle & State Machine
```
States: active → paused → completed

Transitions:
┌─────────────────────────────────────────┐
│          ACTIVE (Running)               │
├─────────────────────────────────────────┤
│ ✅ Can spawn orchestrators              │
│ ✅ Can pull tasks from queue            │
│ ✅ Results are merged                   │
│ ✅ Transition: pause() or complete()    │
└─────────────────────────────────────────┘
         ↓ pause()                    ↓ complete()
         │                             │
┌─────────────────────────────────────────┐  ┌──────────────────────────┐
│        PAUSED (Frozen)                  │  │   COMPLETED (Done)       │
├─────────────────────────────────────────┤  ├──────────────────────────┤
│ ❌ Cannot spawn orchestrators           │  │ ❌ No new orchestrators  │
│ ❌ Queue frozen (tasks not pulled)      │  │ ❌ Queue frozen          │
│ ⚠️  Existing orch still running         │  │ ⚠️  Final results saved  │
│ ✅ Transition: resume()                 │  │ 🔒 FINAL STATE           │
└���────────────────────────────────────────┘  └──────────────────────────┘
         ↑                                      
         └──── resume()
```

---

## 🔐 SESSION RUN MODES & PERMISSIONS

### Development Mode (Dual Orchestrators)
```
SessionScope [mode=development]

Orchestrator-Plan (Planning Context)
├─ Permissions (Read-Only Code + Limited Write)
│  ├─ Read: $(pwd) (project code, config)
│  ├─ Write: $(pwd)/.css/plan/ only
│  ├─ Permission model: Code analysis, no modifications
│  └─ Scope: Planning decisions, architecture, proposals
│
├─ Output Paths
│  ├─ Proposals written to: $(pwd)/.css/sessions/session-<sid>/plan/
│  ├─ Decisions logged: $(pwd)/.css/sessions/session-<sid>/plan/decisions/
│  └─ Analysis output: $(pwd)/.css/sessions/session-<sid>/plan/analysis/
│
└─ Use Cases
   ├─ Architectural review
   ├─ Feature design proposals
   ├─ Code audit & analysis
   └─ Implementation planning

Orchestrator-Dev (Development Context)
├─ Permissions (Full Project Access)
│  ├─ Read: $(pwd) (full project)
│  ├─ Write: $(pwd) (full project)
│  ├─ Permission model: Full execution capability
│  └─ Scope: Implement, test, modify code
│
├─ Output Paths
│  ├─ Code changes: $(pwd)/src/, $(pwd)/tests/
│  ├─ Test results: $(pwd)/.css/sessions/session-<sid>/results/
│  └─ Artifacts: $(pwd)/.css/sessions/session-<sid>/
│
└─ Use Cases
   ├─ Feature implementation
   ├─ Code modifications
   ├─ Testing & verification
   └─ Bug fixes

Communication Flow
Orchestrator-Plan → Decision Queue → Orchestrator-Dev
                    [Review/Approval Gate (optional)]
                    → Execution

Isolation Benefits
✅ Plan orchestrator cannot modify code (safe analysis)
✅ Dev orchestrator implements reviewed decisions
✅ Separation of concerns (plan vs execute)
✅ Audit trail: decisions → implementations
✅ Safe code review workflow
```

### Red Team Mode
```
SessionScope [mode=red_team]

Single Orchestrator (Attack Context)
├─ Permissions: Full project/system access
├─ Scope: Penetration testing, vulnerability discovery
├─ Output: Attack vectors, exploits, findings
└─ Tasks: Simulate attacker behavior
```

### Blue Team Mode
```
SessionScope [mode=blue_team]

Single Orchestrator (Defense Context)
├─ Permissions: Full project/system access
├─ Scope: Detection, remediation, hardening
├─ Output: Defenses, patches, mitigations
└─ Tasks: Simulate defender behavior
```

### Purple Team Mode
```
SessionScope [mode=purple_team]

Dual Orchestrators (Red + Blue Coordination)
├─ Orchestrator-Red
│  ├─ Role: Attack simulation
│  ├─ Permissions: Full access
│  └─ Output: Attack findings
│
└─ Orchestrator-Blue
   ├─ Role: Defense response
   ├─ Permissions: Full access
   └─ Output: Defense measures
   
Shared Results Queue
├─ Red findings → Blue response
├─ Coordinated assessment
└─ Comprehensive security evaluation
```

### Permission Model Architecture
```python
@dataclass
class OrchestratorPermissions:
    """Define what an orchestrator can access"""
    read_paths: List[str]       # e.g., ["/project", "/config"]
    write_paths: List[str]      # e.g., ["/project/.css/plan"]
    
    # Examples:
    # Plan mode:
    #   read: ["/project"]
    #   write: ["/project/.css/plan"]
    #
    # Dev mode:
    #   read: ["/project"]
    #   write: ["/project"]
    #
    # Red/Blue/Purple:
    #   read: ["/project", "/system"]
    #   write: ["/project", "/system"]
```

---

### New Tables

#### teams
```sql
CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    team_type VARCHAR(50) DEFAULT 'general',
    max_concurrent_orchestrators INTEGER DEFAULT 3,
    orchestrator_timeout_sec INTEGER DEFAULT 300,
    orchestrator_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active',      -- active | paused | completed
    priority INTEGER DEFAULT 1,               -- 1-10
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    deleted_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id),
    UNIQUE(session_id, name)
);

CREATE INDEX idx_teams_session_status ON teams(session_id, status);
CREATE INDEX idx_teams_priority ON teams(priority DESC);
```

#### orchestrator_instances
```sql
CREATE TABLE orchestrator_instances (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL,
    team_id INTEGER,                         -- NULL if no teams
    process_id VARCHAR(255),                 -- UUID or PID
    status VARCHAR(50) DEFAULT 'active',     -- active | crashed | inactive
    heartbeat_at TIMESTAMP,
    assigned_task_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    FOREIGN KEY (session_id) REFERENCES sessions(id),
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

CREATE INDEX idx_orch_session ON orchestrator_instances(session_id);
CREATE INDEX idx_orch_team ON orchestrator_instances(team_id, status);
CREATE INDEX idx_orch_heartbeat ON orchestrator_instances(heartbeat_at);
```

#### task_assignments
```sql
CREATE TABLE task_assignments (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL,
    team_id INTEGER,                         -- NULL if no teams
    orchestrator_id INTEGER,
    task_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',    -- pending | assigned | completed | failed
    idempotency_key VARCHAR(255),            -- Prevent duplicate execution
    created_at TIMESTAMP DEFAULT now(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    result_data JSONB,
    FOREIGN KEY (session_id) REFERENCES sessions(id),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (orchestrator_id) REFERENCES orchestrator_instances(id),
    UNIQUE(idempotency_key)
);

CREATE INDEX idx_tasks_session ON task_assignments(session_id, status);
CREATE INDEX idx_tasks_team ON task_assignments(team_id, status);
CREATE INDEX idx_tasks_orch ON task_assignments(orchestrator_id, status);
```

---

## 🎯 ORCHESTRATOR DELEGATION ARCHITECTURE

### Orchestrator as Team Manager
```
Main Orchestrator (Master Process)
│
├─ [Decision Engine]
│  ├─ Parse task requirements
│  ├─ Select agents (from registry)
│  └─ Choose delegation strategy
│
├─ [Team Manager]
│  ├─ Create/destroy teams (independent processes)
│  ├─ Manage team leaders (Team-Leader protocol)
│  └─ Route results back
│
└─ [Agent Loader]
   ├─ Hotload agent files (dynamic import)
   ├─ Maintain agent registry
   └─ Support agent versioning
```

### Team Creation & Process Isolation
```
Orchestrator.spawn_team(name="analysis", context={...})
│
├─ 1. Create Team metadata
├─ 2. Spawn subprocess
│     └─ New Python process (isolated)
│        ├─ Own event loop (asyncio)
│        ├─ Own memory space
│        ├─ Own file descriptors
│        └─ Own context (isolated)
│
├─ 3. Initialize Team Leader (in subprocess)
│     ├─ Listen on communication channel (pipe/socket)
│     ├─ Receive agent delegations
│     └─ Send results back
│
└─ 4. Return Team object
    ├─ team_id
    ├─ process_id
    ├─ communication_channel
    └─ team_leader_protocol
```

### Team Leader Communication Protocol
```
Orchestrator ←→ Team Leader (subprocess)

Messages (async channel: pipe/socket):

1. DELEGATE Agent Task
   Orchestrator → Team:
   {
     "type": "delegate_agent",
     "agent_type": "forensic_analyzer",
     "params": {...},
     "delegation_mode": "async",  # or "sync"
     "callback_id": "task-123"
   }
   
   Team Leader:
   ├─ Load agent (if not cached)
   ├─ Execute in isolated context
   └─ Send result back (with callback_id)

2. Result Notification
   Team → Orchestrator:
   {
     "type": "result",
     "callback_id": "task-123",
     "status": "success",
     "result": {...}
   }

3. Status Update
   Team → Orchestrator:
   {
     "type": "status",
     "team_id": "team-1",
     "status": "active" | "busy" | "idle" | "crashed"
   }

4. Heartbeat
   Team → Orchestrator:
   {
     "type": "heartbeat",
     "team_id": "team-1",
     "timestamp": now()
   }

5. Shutdown
   Orchestrator → Team:
   {
     "type": "shutdown",
     "graceful": true | false
   }
```

### Delegation Modes

#### Mode 1: Async Delegation (Fire & Forget)
```python
# Pseudo-code
result = await team_leader.delegate_agent(
    agent_type="analyzer",
    params={"target": "file.log"},
    mode="async"  # Non-blocking
)

# Immediately returns result object (not the actual result)
# Actual result delivered via callback when ready
```

**Flow**:
```
Orchestrator.delegate("async")
│
├─ 1. Send delegation message to Team
├─ 2. Continue (don't wait)
├─ 3. Receive result callback when ready
└─ 4. Process result asynchronously
```

**Use Cases**:
- Long-running analysis
- Parallel agent execution
- Multiple teams working simultaneously

#### Mode 2: Sync Delegation (Wait for Result)
```python
# Pseudo-code
result = await team_leader.delegate_agent(
    agent_type="analyzer",
    params={"target": "file.log"},
    mode="sync"  # Blocking
)

# Waits until result is ready (with timeout)
```

**Flow**:
```
Orchestrator.delegate("sync")
│
├─ 1. Send delegation message to Team
├─ 2. WAIT for result (blocking)
├─ 3. Receive result
└─ 4. Process result (continue)
```

**Use Cases**:
- Quick synchronous checks
- Dependencies (need result before next step)
- Sequential workflows

### Agent Hotloading Mechanism
```
Agent Registry (Orchestrator)
├─ agent_type → module_path
├─ forensic_analyzer → src/css/agents/forensic_analyzer.py
├─ threat_detector → src/css/agents/threat_detector.py
└─ ...

Hotload Flow:
1. Orchestrator.delegate(agent_type="forensic_analyzer", ...)
2. Team Leader receives delegation
3. Check registry: forensic_analyzer → src/css/agents/forensic_analyzer.py
4. Dynamically import (first time) or use cached
5. Instantiate agent class
6. Execute agent.run(params)
7. Return result

Dynamic Import Example:
spec = importlib.util.spec_from_file_location("module", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
agent = module.AgentClass(**config)
result = await agent.run(params)
```

### Agent Versioning (Future)
```
Agents can have versions:
src/css/agents/forensic_analyzer.py
src/css/agents/forensic_analyzer_v2.py
src/css/agents/forensic_analyzer_v3.py (latest)

Delegation with version:
await team_leader.delegate_agent(
    agent_type="forensic_analyzer",
    version="3",  # or "latest"
    params={...}
)
```

### Example: Multi-Team Forensic Investigation
```
Scenario: Analyze suspicious process logs

Main Orchestrator
├─ Task: "Analyze logs from suspicious process"
├─ Strategy: Create 3 teams, each analyzing differently
│
├─ Create Team-1 (Process Analysis)
│  ├─ Delegate: forensic_analyzer (async)
│  │  └─ Team-1 → Analyze process behavior
│  │     └─ Result: Process timeline, syscalls
│  │
│  └─ Delegate: anomaly_detector (async)
│     └─ Team-1 → Detect anomalies
│        └─ Result: Anomalies found
│
├─ Create Team-2 (Threat Intelligence)
│  ├─ Delegate: ioc_correlator (async)
│  │  └─ Team-2 → Correlate with IOCs
│  │     └─ Result: IOC matches
│  │
│  └─ Delegate: threat_ranker (async)
│     └─ Team-2 → Rank threats
│        └─ Result: Risk scores
│
├─ Create Team-3 (Evidence Collection)
│  └─ Delegate: evidence_collector (sync)
│     └─ Team-3 → Collect evidence
│        └─ Result: Evidence chain (wait for)
│
└─ [All teams running in parallel]
   ├─ Team-1 result ready → Process
   ├─ Team-2 result ready → Process
   ├─ Team-3 result ready → Process (waited for)
   └─ Aggregate results → Final report
```

---

## 🛠️ TOOLS REFERENCE (What SDKs Provide Access To)

### Tool Categories & Descriptions

#### Core System Tools
| Tool | Description | Type |
|------|-------------|------|
| **Terminal/Bash** | Execute shell commands in project scope | Execution |
| **File System** | Read/write files in project directories | I/O |
| **Subprocess** | Spawn child processes with isolation | Execution |

#### Data & Analysis Tools
| Tool | Description | Type |
|------|-------------|------|
| **Database** | Query PostgreSQL (findings, IOCs, compliance, etc.) | Data |
| **Cache Lookup** | Retrieve cached data (tokens, responses, memory) | Data |
| **Cache Store** | Persist data to Redis cache | Data |
| **Memory Search** | Vector search in AI memory (semantic queries) | Data |
| **Memory Add** | Store findings/insights in AI memory | Data |

#### Findings & IOC Management
| Tool | Description | Type |
|------|-------------|------|
| **Add Finding** | Create vulnerability/security finding | Data |
| **Query Findings** | Search findings by criteria | Data |
| **Add IOC** | Create Indicator of Compromise | Data |
| **Query IOCs** | Search IOC database | Data |
| **Risk Register** | Update risk tracking | Data |

#### Intelligence & MITRE Mapping
| Tool | Description | Type |
|------|-------------|------|
| **Suggest MITRE** | Map findings to MITRE ATT&CK techniques | Intelligence |
| **Query PoCs** | Search Proof-of-Concept records | Intelligence |
| **Add PoC** | Store new PoC/exploit record | Intelligence |

#### AI Proxy & LLM Management
| Tool | Description | Type |
|------|-------------|------|
| **Proxy Chat** | Call multi-provider LLM (auto/free/preferred routing) | LLM |
| **List Models** | Get catalog of available models + pricing | LLM |
| **Get Usage** | Query token/cost usage by provider/session | LLM |
| **Get Cost** | Calculate cost for predicted tokens | LLM |
| **Set Budget Guard** | Enforce spending limit per provider | LLM |
| **Simulate Route** | Test routing strategy without executing | LLM |

#### Session & Orchestration
| Tool | Description | Type |
|------|-------------|------|
| **Session Snapshot** | Capture current session state | Metadata |
| **Agent Registry** | List active agents + capabilities | Metadata |
| **Best Provider** | Recommend optimal provider for task | Metadata |

#### Web & External Tools
| Tool | Description | Type |
|------|-------------|------|
| **Web Fetch** | Retrieve HTML/JSON from URLs | External |
| **Web Search** | Query internet (Perplexity/Serper/Brave/Tavily) | External |

#### Cryptography Tools
| Tool | Description | Type |
|------|-------------|------|
| **Sign** | Ed25519 cryptographic signing | Crypto |
| **Verify** | Verify Ed25519 signatures | Crypto |
| **Hash** | BLAKE2b content hashing | Crypto |
| **Encrypt** | AES-256-GCM authenticated encryption | Crypto |
| **Decrypt** | AES-256-GCM authenticated decryption | Crypto |

#### Output & Configuration
| Tool | Description | Type |
|------|-------------|------|
| **QoL Get** | Get current output control toggles | Config |
| **QoL Set** | Update output toggles (silent, code-only, audit, etc.) | Config |
| **QoL Reset** | Restore default QoL settings | Config |
| **QoL Presets** | List/apply bundled toggle combinations | Config |

#### Case Management
| Tool | Description | Type |
|------|-------------|------|
| **Case Open** | Create new investigation case | Data |
| **Case Status** | Query case metadata & status | Data |

### SDK Access Model

Different SDKs provide different tool subsets:

| SDK | Tools Available |
|-----|-----------------|
| **csscore-mcp** | Database, findings, IOCs, cases, PoCs, intelligence |
| **dystopian-crypto-mcp** | Sign, verify, hash, encrypt, decrypt |
| **ai-proxy-mcp** | Proxy chat, list models, usage, cost, budget, simulate |
| **memory-mcp** | Memory search, memory add, memory clear |
| **canvas-mcp** | File system, visualization tools |
| **playwright-mcp** | Web fetch, web automation |
| **web-search-mcp** | Web search (Perplexity/Serper/Brave/Tavily) |
| **custom-mcp** | User-provided custom tools |

### Execution Context

All tools execute within **Role + Scope isolation**:
- ✅ Tool execution scoped to project/session/team boundaries
- ✅ Permissions checked via role's granted tool set
- ✅ Async execution with timeout limits
- ✅ Results captured for audit trail

---

## 🛠️ COMPLETE SDK TOOLS REFERENCE (All Providers)

### Anthropic Claude SDK
| Tool | Type | Description |
|------|------|-------------|
| **Tool Use (Function Calling)** | function_calling | Client-side custom tools with full control via JSON schema |
| **Web Search** | execution | Real-time web search integration |
| **Web Fetch** | web | Retrieve full web page/PDF content from URLs |
| **Code Execution** | execution | Sandboxed Python code execution |
| **Computer Use** | interaction | Screenshot, mouse, keyboard control (Beta) |
| **Text Editor** | file | Create/edit text files |
| **Bash** | execution | Execute bash commands |
| **Memory** | state | Store/retrieve conversation context |
| **Advisor Tool** | orchestration | Pair fast executor with strategic advisor (Beta) |
| **Agent Skills** | orchestration | Pre-built skills (PowerPoint, Excel, Word, PDF) |

### OpenAI SDK
| Tool | Type | Description |
|------|------|-------------|
| **Function Calling** | function_calling | GPT function calling via tools + tool_choice |
| **Chat Completions** | chat | Core chat endpoint with tool support |
| **Vision/Image Input** | multimodal | Process images in messages (base64 or URL) |
| **Batch API** | execution | Asynchronous batch processing |
| **File Upload** | file | Upload files for analysis |
| **Embeddings** | embedding | Text embeddings generation |
| **Audio Transcription** | execution | Whisper model transcription |
| **Text-to-Speech** | execution | Generate speech from text |

### Google Gemini SDK
| Tool | Type | Description |
|------|------|-------------|
| **Function Calling** | function_calling | Define function declarations with JSON schema |
| **Google Search** | execution | Real-time web search integration |
| **Google Maps** | execution | Maps integration for location data |
| **Code Execution** | execution | Run Python code in sandbox |
| **URL Context** | web | Retrieve and process URL content |
| **Computer Use** | interaction | GUI automation via screenshots (Experimental) |
| **File Search** | file | Search within uploaded documents |
| **Deep Research Agent** | orchestration | Multi-step research agent |
| **Live API Tools** | realtime | Real-time tool use in streaming (Beta) |
| **Imagen** | generation | Image generation from text |
| **Lyria 3** | generation | Music generation from text (Beta) |
| **Veo** | generation | Video generation from text (Beta) |

### Mistral SDK
| Tool | Type | Description |
|------|------|-------------|
| **Function Calling / Tool Calling** | function_calling | Custom tools with JSON schema validation |
| **Agents** | orchestration | Agentic workflows and loops |

### Groq SDK (OpenAI-Compatible)
| Tool | Type | Description |
|------|------|-------------|
| **Function Calling** | function_calling | OpenAI-compatible format via baseURL override |
| **Chat Completions** | chat | OpenAI-compatible chat endpoint |
| **Fast Inference** | execution | Optimized low-latency inference |

### Together AI SDK (OpenAI-Compatible)
| Tool | Type | Description |
|------|------|-------------|
| **Vision API** | multimodal | Image and OCR processing |
| **Function Calling** | function_calling | OpenAI-compatible tools format |
| **Chat Completions** | chat | OpenAI-compatible chat |
| **Batch Processing** | execution | Large batch job execution |
| **Fine-tuning** | training | Model fine-tuning on custom data |

### DeepSeek SDK (OpenAI-Compatible)
| Tool | Type | Description |
|------|------|-------------|
| **Function Calling** | function_calling | OpenAI-compatible tools format |
| **Chat Completions** | chat | OpenAI API compatible |
| **Reasoning** | execution | DeepSeek-R1 extended thinking mode |

### xAI Grok SDK (OpenAI-Compatible)
| Tool | Type | Description |
|------|------|-------------|
| **Function Calling** | function_calling | Likely OpenAI-compatible (docs restricted) |
| **Chat Completions** | chat | OpenAI API format |

### OpenRouter SDK
| Tool | Type | Description |
|------|------|-------------|
| **Client SDK** | client | Type-safe wrapper for unified API |
| **Agent SDK** | orchestration | Tool execution and state management (Zod schemas) |
| **Function Calling** | function_calling | Tool definitions via Zod validation |
| **OpenAI Compatibility** | client | Drop-in replacement with baseURL override |
| **REST API** | http | Direct `/api/v1/chat/completions` endpoint |
| **Model Fallback** | orchestration | Automatic fallback between models |
| **Cost Optimization** | orchestration | Select most cost-effective models |

### Capability Comparison Matrix

| Capability | Anthropic | OpenAI | Google | Mistral | Groq | Together | DeepSeek | xAI | OpenRouter |
|-----------|-----------|--------|--------|---------|------|----------|----------|-----|-----------|
| Function Calling | ✅ GA | ✅ GA | ✅ GA | ✅ GA | ✅ | ✅ | ✅ | ✅ | ✅ GA |
| Web Search | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Code Execution | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Vision/Images | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Audio I/O | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Video Gen | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Computer Use | ✅ β | ❌ | ✅ ⚠ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Memory/Context | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Batch API | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Extended Thinking | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Agent Orchestration | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Parallel Tool Calls | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Legend**: ✅ = GA (General Availability) | β = Beta | ⚠ = Experimental | ❌ = Not Available

### Integration Notes
- **Function Calling Standard**: All 9 providers support it; use native format (avoid transpilation)
- **OpenAI-Compatible**: Groq, Together, DeepSeek, xAI use OpenAI format + baseURL override
- **Server-side Execution**: Anthropic & Google offer server-side tool execution; others require client-side
- **Agentic Support**: Only Anthropic, Google, Mistral, and OpenRouter have managed agent infrastructure
- **Parallel Tools**: All providers support parallel tool calling

---

## 🔗 RELATED DOCUMENTATION

- **plan.md** — Timeline, milestones, status
- **features_overview.md** — Feature specs, APIs, success criteria
- **workflow.md** — Development process, todo tracking
- **rules.md** — Tech stack, project structure, scope filesystem

---

**Status**: Architecture finalized  
**Next**: Phase 0 - TeamScope model implementation

---

## SDK & Module Architecture (NEW)

### 4-Layer SDK Architecture

```
Layer 4: UniversalLLMClient (Router)
    ├─ Official SDKs (anthropic, openai, groq, etc.)
    ├─ REST-Mapped Providers (deepseek, perplexity, etc.)
    ├─ Local Models (ollama)
    └─ Browser-Based (webllm)

Layer 3: Unified REST Client (REST-only providers)
    ├─ request_mapper.py (generic → provider format)
    ├─ response.py (provider format → generic)
    └─ error_handler.py

Layer 2: Custom SDKs (4 types)
    ├─ Unified REST Client
    ├─ Ollama Local SDK
    ├─ WebLLM Browser SDK
    └─ response.py Pattern (all 24 providers)

Layer 1: response.py Pattern (all providers)
    ├─ map_to_provider_request()
    ├─ parse_stream_chunk()
    └─ handle_error()
```

### Module Pattern (19 modules + 8 core subdirs)

Every module/subdir must have:
```
module_name/
├── __init__.py           # Package marker
├── models.py             # Tortoise ORM models (auto-discovered)
├── endpoints.py          # FastAPI router (auto-discovered)
├── enums.py              # Module enumerations (auto-discovered)
├── types.py              # Dataclasses & types (auto-discovered)
└── exceptions.py         # Custom exceptions (auto-discovered)
```

**Modules applying pattern**: 19 in css/modules/ (95 files missing)  
**Core applying pattern**: 8 subdirs in css/core/ (28 files missing)

### Loader.py Enhancement

Current auto-discovery:
- modules/*/models.py ✓
- modules/*/endpoints.py ✓
- api_services/*/models.py ✓

Proposed additions:
- core/*/types.py (NEW)
- core/*/enums.py (NEW)
- core/*/exceptions.py (NEW)
- modules/*/types.py (NEW)
- modules/*/enums.py (NEW)
- modules/*/exceptions.py (NEW)

Benefits:
- Consistency enforcement at startup
- Type discovery for orchestrator
- Early error detection (fail-fast)
- Foundation for multi-process delegation

---

## Implementation Phases (Updated)

### Phase 0: Foundation Setup
- [x] TeamScope model design
- [x] Database schema finalized
- [ ] Create TeamScope models.py

### Phase 1: Pattern Consistency (PARALLEL)
- [ ] Track 2: response.py + SDKs (15 todos)
- [ ] Track 3: Module pattern (42 todos)
- [ ] Track 4: Core pattern (38 todos)

### Phases 2-6: Multi-Orchestrator Implementation
- [ ] Phase 1-6 todos for multi-orch + TeamScope (10 todos)

**Total Implementation**: 115 todos across 4 parallel tracks

---

## 🔄 core/types/ Restructuring Analysis

**Current Structure** (953 lines across 20 files):

```
core/types/
├── __init__.py           # Re-exports from base/, capabilities, context, entities, headers
├── api_services.py       # API service registry (43 lines)
├── capabilities.py       # CapabilityRegistry + ModelCapabilities (156 lines)
├── context.py            # Conversation/Execution/Model contexts (187 lines)
├── headers.py            # Provider-specific headers (94 lines)
├── hook_events.py        # Event hook definitions (82 lines)
├── sdk_local.py          # Local SDK types (41 lines)
├── base/                 # Base classes & protocols
│   ├── base_client.py    # BaseApiServiceClient (122 lines)
│   ├── base_context.py   # BaseContext (91 lines)
│   ├── base_entity.py    # BaseEntity + ABC violations (158 lines)
│   ├── base_header.py    # BaseHeader (96 lines)
│   ├── base_protocols.py # Protocol definitions (121 lines)
│   ├── base_registry.py  # Registry base class (61 lines)
│   └── __init__.py       # Re-exports (17 lines)
├── entities/             # Business entities (moved from distributed modules)
│   ├── account.py        # Account entity (73 lines)
│   ├── agent.py          # Agent entity (126 lines)
│   ├── role.py           # Role entity (84 lines)
│   ├── skill.py          # Skill entity (97 lines)
│   ├── tool.py           # Tool entity (144 lines)
│   └── __init__.py       # Re-exports (78 lines)
└── __pycache__/
```

**Current Problems**:
1. Entities consolidated in core/ (should move to modules/*/types.py)
2. Provider-specific files (api_services.py, headers.py) mixed with core abstractions
3. base_entity.py mixes ABC + @dataclass (inconsistent pattern)
4. Future Phase 2: Will need core/types/providers/ subdirectory (24+ providers)
5. No clear separation: core infrastructure vs business domain vs provider-specific

---

## 🎯 3 Restructuring Options

### OPTION A: Minimal Restructuring (Backward Compatible)

**Keep current structure, only add providers/ subdirectory**

```
core/types/
├── base/
│   ├── base_client.py
│   ├── base_context.py
│   ├── base_entity.py
│   ├── base_header.py
│   ├── base_protocols.py
│   ├── base_registry.py
│   └── __init__.py
├── entities/
│   ├── account.py → MOVE to modules/accounts/types.py
│   ├── agent.py → MOVE to modules/agents/types.py
│   ├── role.py → MOVE to modules/permissions/types.py
│   ├── skill.py → MOVE to modules/skills/types.py
│   ├── tool.py → MOVE to modules/tools/types.py
│   └── __init__.py (deprecated)
├── providers/          # NEW for Phase 2
│   ├── base_providers.py
│   ├── headers/
│   └── [24 provider subdirs]
├── api_services.py
├── capabilities.py
├── context.py
├── headers.py
├── hook_events.py
├── sdk_local.py
└── __init__.py
```

**Pros**:
- ✅ Minimal changes to existing code
- ✅ Easy to merge (just add providers/)
- ✅ Phase 2 can proceed without refactoring
- ✅ Entities can migrate gradually (optional)

**Cons**:
- ❌ Entities still in core/ (wrong place)
- ❌ core/types/ becomes bloated (~50+ files by Phase 2)
- ❌ Doesn't fix ABC + @dataclass violations
- ❌ Provider concerns mixed with core abstractions
- **Effort**: Low (1-2 days)

---

### OPTION B: Aggressive Reorganization (Clean Architecture)

**Separate core infrastructure → provider-specific → business domain**

```
core/types/
├── base/
│   ├── base_protocols.py    # Pure protocols (no ABC violations)
│   ├── base_context.py
│   ├── base_registry.py
│   └── __init__.py
├── infrastructure/          # NEW: Core-only abstractions
│   ├── base_client.py       # Rename from base/
│   ├── base_entity.py       # FIXED: Remove ABC violations
│   ├── base_header.py
│   └── __init__.py
├── api_core/                # NEW: API-layer abstractions (not provider-specific)
│   ├── capabilities.py      # MOVE: Re-export from here
│   ├── context.py           # MOVE: Re-export from here
│   └── __init__.py
├── providers/               # Phase 2: Provider directory
│   ├── base_providers.py
│   ├── headers/
│   └── [24 provider subdirs]
└── __init__.py (unified re-export)

# Entities distributed:
modules/accounts/types.py
modules/agents/types.py
modules/permissions/types.py
modules/skills/types.py
modules/tools/types.py
```

**Pros**:
- ✅ Clear layer separation: infrastructure → api → providers
- ✅ Entities in correct location (modules/)
- ✅ Can fix ABC violations
- ✅ core/types/ focused on abstractions only
- ✅ Scales to Phase 2+ without bloat

**Cons**:
- ❌ Major refactoring (7-10 days)
- ❌ All imports must change (high risk)
- ❌ Requires comprehensive testing
- ❌ Migration guide needed for existing code
- **Effort**: High (1 week)

---

### OPTION C: Hybrid Approach (Pragmatic Middle Ground)

**Keep base/ and core files, move entities, add providers/ with structure**

```
core/types/
├── base/                    # KEEP as-is
│   ├── base_client.py
│   ├── base_context.py
│   ├── base_entity.py
│   ├── base_header.py
│   ├── base_protocols.py
│   ├── base_registry.py
│   └── __init__.py
├── api_services.py          # KEEP (small, stable)
├── capabilities.py          # KEEP (small, stable)
├── context.py               # KEEP (used by core/ layers)
├── headers.py               # KEEP (small, stable)
├── hook_events.py           # KEEP (small, stable)
├── sdk_local.py             # KEEP (small, stable)
├── providers/               # NEW: Phase 2 provider directory
│   ├── __init__.py
│   ├── base_providers.py    # APIProviderBase, LocalProviderBase
│   ├── headers/             # Provider headers organized
│   │   ├── __init__.py
│   │   └── [provider headers]
│   ├── ollama_provider.py
│   ├── anthropic_provider.py
│   └── [22 more provider subdirs]
└── __init__.py (unified re-export from base/, +providers/)

# Entities distributed gradually (post-Phase 2):
modules/accounts/types.py
modules/agents/types.py
modules/permissions/types.py
modules/skills/types.py
modules/tools/types.py
```

**Pros**:
- ✅ Moderate refactoring (3-4 days)
- ✅ Entities can migrate post-Phase 2 (lower priority)
- ✅ Phase 2 can proceed immediately (providers/ ready)
- ✅ No breaking changes to existing imports (redirect via __init__.py)
- ✅ Scales to Phase 2+ with clear structure
- ✅ Easier code review (smaller PRs)

**Cons**:
- ⚠️ Entities still temporarily in entities/ (accepted technical debt)
- ⚠️ ABC violations in base_entity.py remain (post-Phase 2 fix)
- ⚠️ Two-phase migration (entities move later)
- **Effort**: Medium (3-4 days)

---

## 🎯 RECOMMENDATION

**Choose OPTION C (Hybrid)**

**Rationale**:
1. **Phase 2 blocking**: Providers need structured home immediately
2. **Risk mitigation**: No breaking changes, gradual migration
3. **Effort vs impact**: 3-4 days gets Phase 2 unblocked
4. **Future flexibility**: Entities can move post-Phase 2 without rush
5. **Team velocity**: Smaller PRs, easier reviews

**Implementation Sequence**:
1. Create `core/types/providers/` directory structure
2. Create `core/types/providers/base_providers.py` (APIProviderBase, LocalProviderBase)
3. Create `core/types/providers/headers/` subdirectory
4. Move provider-specific headers to `providers/headers/`
5. Phase 2 proceeds: Move 24 providers into `providers/` subdirs
6. Phase 3+ (post-Phase 2): Move entities to modules/*/types.py

---

## 🔍 DEEP INSPECTION: core/types/ Current State

### File Inventory (1,866 total lines)

**Root files** (668 lines):
- `__init__.py` (119 lines) — Re-exports from base/, entities, capabilities, context, headers, hooks
- `api_services.py` (36 lines) — Registry for API services
- `capabilities.py` (168 lines) — Capability definitions + registry
- `context.py` (146 lines) — Conversation/Execution/Model contexts
- `headers.py` (108 lines) — Provider-specific headers (abstract)
- `hook_events.py` (39 lines) — Event hook definitions
- `sdk_local.py` (338 lines) — Local SDK base class (large!)

**base/** subdirectory (606 lines, 6 files):
- `base_client.py` (277 lines) — BaseApiServiceClient (LARGE, complex)
- `base_entity.py` (165 lines) — ❌ **CRITICAL**: Mixes ABC + @dataclass (violation)
- `base_header.py` (38 lines) — BaseHeader + BaseToolHeader
- `base_registry.py` (99 lines) — Registry base class
- `base_protocols.py` (67 lines) — Protocol definitions
- `__init__.py` (57 lines) — Re-exports from above 5

**entities/** subdirectory (307 lines, 5+1 files):
- `tool.py` (35 lines) — Tool entity
- `skill.py` (42 lines) — Skill entity
- `role.py` (92 lines) — Role entity + factory
- `agent.py` (52 lines) — Agent entity
- `account.py` (59 lines) — Account entity
- `__init__.py` (27 lines) — Re-exports

### Dependency Analysis

**Who imports from core.types?** (4 files, VERY LOW usage!)
1. `api_services/error_mappers.py` — Imports ProviderType
2. `api_services/ollama/compat.py` — Imports ProviderType
3. `core/retry/detection.py` — Imports ProviderType
4. `core/retry/orchestrator.py` — Imports ProviderType

**Entities (Account, Agent, Role, Skill, Tool)**: NO external imports found (!)
- Currently defined in core/types/entities but NOT used outside core/
- Should move to modules/*/types.py where appropriate

**Implication**: LOW external coupling = Safe to restructure

---

## 🎯 3 REVISED Restructuring Options (Fact-Based)

### OPTION A: Minimal + Safe (Low Risk, 2 days)

**Keep entire core/types/ structure as-is. Only prepare for Phase 2.**

```
core/types/                    # UNCHANGED
├── base/
├── entities/
├── api_services.py
├── capabilities.py
├── context.py
├── headers.py
├── hook_events.py
├── sdk_local.py
└── __init__.py

core/types/providers/          # NEW for Phase 2
├── __init__.py
├── base_providers.py          # APIProviderBase, LocalProviderBase
└── headers/                   # Provider-specific headers
```

**Pros**:
- ✅ Zero breaking changes
- ✅ Unblocks Phase 2 immediately
- ✅ Fast to implement (2 days)
- ✅ All existing imports still work
- ✅ Entities can migrate later (post-Phase 2)

**Cons**:
- ❌ core/types becomes large (~100+ files by Phase 2 end)
- ❌ ABC + @dataclass violations remain
- ❌ Entities logically in wrong place
- ⚠️ Technical debt (requires Phase 3+ refactoring)

**Risk**: Low | **Effort**: 2 days | **Recommendation**: ✅ **For immediate Phase 2 unblocking**

---

### OPTION B: Aggressive Cleanup (High Quality, 1 week)

**Fix ABC violations, move entities, reorganize into layers, complete restructure**

**Result**: 4 new subdirectories (base, infrastructure, api_layer, sdk) + entities distributed to modules/ + providers/ for Phase 2

**Pros**:
- ✅ Clean layered architecture
- ✅ Fixes ABC + @dataclass violations
- ✅ Entities in correct location (modules/)
- ✅ core/types focused on abstractions
- ✅ Scales well to Phase 2+

**Cons**:
- ❌ High-risk refactoring (many file moves, import changes)
- ❌ 1 week effort
- ❌ Codebase-wide import changes (all files affected)
- ❌ Could delay Phase 2 (if urgent)
- ❌ Complex code review

**Risk**: High | **Effort**: 1 week | **Recommendation**: ❌ **Too risky if Phase 2 is urgent**

---

### OPTION C: Pragmatic Hybrid ⭐ (Best Trade-off, 3 days)

**Move entities to modules/ (business domain), keep infrastructure in core/types/, add providers/ for Phase 2**

```
core/types/
├── base/                      # KEEP: Unchanged
├── api_services.py            # KEEP: Small, stable
├── capabilities.py            # KEEP: Small, stable
├── context.py                 # KEEP: Used by core/
├── headers.py                 # KEEP: Small, stable
├── hook_events.py             # KEEP: Small, stable
├── sdk_local.py               # KEEP: Stable
│
├── providers/                 # NEW: Phase 2 ready
│   ├── base_providers.py      # APIProviderBase, LocalProviderBase
│   └── headers/               # Provider-specific headers
│
└── __init__.py                # Updated (removes entities)

# Entities distributed immediately:
modules/accounts/types.py      # Account
modules/agents/types.py        # Agent
modules/permissions/types.py   # Role
modules/skills/types.py        # Skill
modules/tools/types.py         # Tool
```

**Actions**:
1. Create modules/*/types.py files (5 files)
2. Move entities from core/types/entities/ to modules/*/types.py
3. Update core/types/__init__.py to re-import from modules/*/types.py
4. Delete core/types/entities/
5. Create core/types/providers/
6. Ruff + pytest

**Pros**:
- ✅ Entities move to correct location (modules/)
- ✅ Phase 2 unblocked (providers/ ready)
- ✅ Moderate effort (3 days)
- ✅ Lower risk than Option B (focused changes)
- ✅ Fixes logical separation (entities out of core)
- ✅ Can parallel-track with Phase 2
- ✅ Defers ABC violation to Phase 3 (acceptable)

**Cons**:
- ⚠️ Circular import potential (modules → core, core → modules)
  - Mitigated via lazy imports or TYPE_CHECKING
- ⚠️ ABC + @dataclass violation remains (deferred to Phase 3)

**Risk**: Medium-Low | **Effort**: 3 days | **Recommendation**: ⭐ **BEST for Phase 2 + architecture**

---

## ✅ FINAL RECOMMENDATION: **OPTION C (Pragmatic Hybrid)**

**Decision Made**: 2026-05-03 — **OPTION C SELECTED**

**Why**:
1. Phase 2 unblocked (providers/ ready)
2. Architectural improvement (entities in modules/)
3. Risk-time balance (3 days, manageable)
4. Parallel workflow (entities + Phase 2 concurrent)
5. Acceptable debt (ABC violation deferred to Phase 3)

**Implementation Sequence**:
1. Create modules/accounts/types.py + move Account
2. Create modules/agents/types.py + move Agent
3. Create modules/permissions/types.py + move Role
4. Create modules/skills/types.py + move Skill
5. Create modules/tools/types.py + move Tool
6. Update core/types/__init__.py to re-import from modules/*/types.py
7. Delete core/types/entities/
8. Create core/types/providers/ directory
9. Ruff + pytest

---

---

