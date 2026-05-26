# @roles — Role Definitions & Management

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This document owns the executable roles specification.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | ORM models (if applicable) |
| `css.core.permissions` | ← consumed by | Role grants constrain path/tool authorization policy. |
| `css.modules.agents` | ← consumed by | Agent role assignment and execution capability checks. |
| `css.modules.teams` | ← consumed by | Team leader/member role semantics. |
| `css.core.events` | → emits | Role assignment/change audit events when wired. |

---

## Current State

🟡 **Skeleton** (method signatures with docstrings, bodies marked `pass`)

---

## Purpose

- Define role hierarchy (Orchestrator, TeamLeader, Worker, Planner, Triage, TeamMember)
- Manage role assignments to users
- Enforce role-based access control
- Support role inheritance
- Provide role querying and filtering

---

## Implementation Checklist

- [x] Role definition classes — OrchestrationRole base with 3 subclasses
- [x] Role registry — REGISTRY dict + get() lookup function
- [x] Role enums — RoleType (3 roles) and Permission (16+ permissions)
- [x] Role exceptions — RoleNotFoundError, PermissionDeniedError, InvalidRoleError
- [x] Role inheritance resolution — Current behavior exists; any touched
  value-type implementation must use `msgspec.Struct` rather than dataclasses.
- [x] Role-to-permission mapping — permissions list on each role
- [x] Add logger initialization in `__init__.py` — Full logging setup

**Completed (Phase 2 Foundation)**:
✅ OrchestrationRole value-type surface with standard fields; touched
implementations must use `msgspec.Struct`.
✅ OrchestratorRole (process-level, 60s heartbeat, 7 permissions)
✅ TeamLeaderRole (in-process, 30s heartbeat, 7 permissions)
✅ TeamMemberRole (executor, 15s heartbeat, 4 permissions)
✅ Built-in role singletons (ORCHESTRATOR, TEAM_LEADER, TEAM_MEMBER)
✅ RoleType enum (3 orchestration roles)
✅ Permission enum (16 permissions)
✅ Exception hierarchy (RoleNotFoundError, PermissionDeniedError)
✅ Full __init__.py exports and logging

---

## Module Pattern

```python
# src/css/modules/roles/__init__.py
"""Role definitions and management."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .role_types import OrchestratorRole, TeamLeaderRole, WorkerRole

__all__ = ['OrchestratorRole', 'TeamLeaderRole', 'WorkerRole']
```

---

**Status**: 🔴 Priority (High) | **Last Updated**: 2026-05-03
## 🎭 ROLE ABSTRACTION LAYER

### Role Types (6 Total)

**All orchestration roles:**
1. **Planner** — Planning & analysis (read-only project, write proposals/decisions)
2. **Orchestrator** — Main orchestration (full project access, delegates to teams)
3. **TeamLeader** — Team coordination (manages workers/team members in subprocess)
4. **Worker** — Task execution (executes agents, performs actual work)
5. **Triage** — Background routing (routes tasks, prioritizes, always-on)
6. **TeamMember** — Team agent (individual worker/agent in team)

**Process Mapping:**

```
Development Mode (3 Separate Processes)
├─ Process 1: Planner role
├─ Process 2: Orchestrator role (main)
└─ Process 3: Triage role (background)

Red/Blue/Purple Modes (2 Separate Processes)
├─ Process 1: Orchestrator role (main)
└─ Process 2: Triage role (background)

Team Subprocess (Per Team)
├─ TeamLeader role
├─ Worker roles (N agents/workers)
└─ TeamMember roles (individual team members)
```

### Concept: Unified Capability Stack

**Role** is the top-level abstraction that unifies all capability types:

```
┌─────────────────────────────────────────┐
│           ROLE (Persona/Skill)          │
│  (Unified abstraction layer)            │
│                                         │
│  Planner | Orchestrator | TeamLeader    │
│  Worker  | Triage       | TeamMember    │
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
class Role(msgspec.Struct, frozen=True):
    """Role = unified capability across agents, skills, tools, MCPs"""
    role_id: str           # e.g., "senior-engineer"
    agents: list[Agent]    # Which agents can this role spawn?
    skills: list[Skill]    # Which skills are attached?
    tools: list[Tool]      # Which tools can it call?
    sdk_access: dict[str, object]  # Which MCPs/SDKs are available?
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

**Key Principle**: ALL orchestrators run in separate processes, never co-located.

```
Orchestrator Process Layout (Mode-Dependent)

DEVELOPMENT MODE (Up to 3 Separate Processes)
│
├─ Process 1 (PID: 1001): Planner Orchestrator
│  ├─ Role: Planning & decision making
│  ├─ Access: Read-only project scope, write to plan/ only
│  ├─ Capability: Can delegate to planning teams
│  └─ Output: Proposals, decisions (to plan/)
│
├─ Process 2 (PID: 1002): Normal Orchestrator (Main)
│  ├─ Role: Primary execution
│  ├─ Access: Full project scope (read/write)
│  ├─ Capability: Execute tasks, create teams, spawn orchestrators
│  └─ Output: Code changes, results
│
└─ Process 3 (PID: 1003): Background Orchestrator (Triage/Routing)
   ├─ Model: Qwen3-0.6B (lightweight, always-on)
   ├─ Role: Background task triage & routing
   ├─ Access: Read project scope, limited write (logs)
   ├─ Capability: Route tasks to appropriate teams/processes
   └─ Output: Task routing decisions


OTHER MODES (Red/Blue/Purple) (2 Separate Processes)
│
├─ Process 1 (PID: 2001): Main Orchestrator
│  ├─ Role: Primary execution (attack/defense/both)
│  ├─ Access: Full project scope (read/write)
│  ├─ Capability: Execute tasks, create teams, spawn orchestrators
│  └─ Output: Results, findings, mitigations
│
└─ Process 2 (PID: 2002): Background Orchestrator (Triage/Routing)
   ├─ Model: Qwen3-0.6B (lightweight, always-on)
   ├─ Role: Background task triage & routing
   ├─ Access: Read project scope, limited write (logs)
   ├─ Capability: Route tasks to appropriate teams/processes
   └─ Output: Task routing decisions


TEAM DELEGATION PATTERN
│
Main Orchestrator (Process)
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
- **Process Hierarchy**: Each orchestrator in separate process (main orchestrators + delegated teams)
- **Each Main Orchestrator**: Has own isolated process, full Project Scope access
- **Delegated Teams**: Run in separate subprocess with isolated context, must report back
- **Communication**: Parent-child IPC (pipe/socket) for delegation & results
- **Isolation Guarantee**: Crash in one orchestrator process ≠ crash in another

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
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: Query `.plan/session.db` for current status; retain role implementation detail in this local document.

---

## 🔄 Sync Reminder

> **STATUS AUTHORITY**: Query `.plan/session.db` for live todo progress.
>
> - This file defines the implementation contract, not completion state.
> - Update tracker state as required by `.plan/rules.md`.
> - **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE
> - See `.plan/rules.md` CRITICAL section for full rules
>
> **Pattern rules enforced here**:
> - `__all__` lives ONLY in `__init__.py` (never in types.py, enums.py, endpoints.py)
> - Never mix `@dataclass` with `ABC` on the same class
> - Use `msgspec.Struct` for value types, `Protocol` for structural contracts (Phase 6)
> - HTTP clients: always `aiohttp`, never `httpx`
> - Package manager: always `uv`/`bun`, never `pip`/`npm`
