# CyberSecSuite Architecture

**Status**: 🏗️ Detailed System Design  
**Updated**: 2026-05-03  
**Scope**: Multi-Orchestrator + TeamScope implementation

---

## 📐 SYSTEM OVERVIEW

### Execution Model: Main Processes by Mode

**Key Principle**: ALL orchestrators run in separate, isolated processes (never co-located).

#### Development Mode (Up to 3 Separate Processes)
```
Session [mode=development]

Process 1 (PID: 1001): Planner Orchestrator
├─ Role: Planning & decision making
├─ Access: Read-only project code
├─ Output: Proposals, decisions (to .css/plan/)
├─ Model: LLM (for planning)
├─ Isolation: Full process isolation
└─ Capability: Delegate to planning teams

Process 2 (PID: 1002): Normal Orchestrator (Main)
├─ Role: Primary execution
├─ Access: Full project scope (read/write)
├─ Output: Code changes, results
├─ Model: LLM (for implementation)
├─ Isolation: Full process isolation
└─ Capability: Execute tasks, create teams, spawn subprocesses

Process 3 (PID: 1003): Background Orchestrator (Triage)
├─ Model: Qwen3-0.6B (lightweight, always-on)
├─ Role: Task triage & routing
├─ Access: Read project, limited write (logs)
├─ Isolation: Full process isolation
└─ Capability: Route tasks to appropriate teams/processes
```

#### Other Modes: Red/Blue/Purple (2 Separate Processes)
```
Session [mode=red_team|blue_team|purple_team]

Process 1 (PID: 2001): Main Orchestrator
├─ Role: Attack/Defense/Coordinated execution
├─ Access: Full project scope (read/write)
├─ Output: Findings, results, mitigations
├─ Model: LLM (for simulation)
├─ Isolation: Full process isolation
└─ Capability: Execute tasks, create teams, spawn subprocesses

Process 2 (PID: 2002): Background Orchestrator (Triage)
├─ Model: Qwen3-0.6B (lightweight, always-on)
├─ Role: Task triage & routing
├─ Access: Read project, limited write (logs)
├─ Isolation: Full process isolation
└─ Capability: Route tasks to appropriate teams/processes
```

### Main Orchestrator Capabilities

**Role Types (6 total):**
1. **Planner** — Planning & analysis (read-only code, proposals/decisions)
2. **Orchestrator** — Main process, delegates to teams, manages execution
3. **TeamLeader** — Coordinates agents/workers within team subprocess
4. **Worker** — Executes tasks, runs agents, performs work
5. **Triage** — Routes tasks, prioritizes, background processing
6. **TeamMember** — Individual agent/worker in team

Each orchestrator process integrates **`@cache` module** for:
- **Task Result Caching** (idempotency keys prevent re-execution)
- **LLM Response Caching** (reduce Claude API costs 40-60%)
- **Orchestrator Heartbeat** (Redis cache for crash detection)

```
Main Orchestrator Process
├─ Access: Full Project Scope ($(pwd)/)
├─ Cache Layer: @cache module (multi-level backends)
│  ├─ L1: In-Memory (session-local)
│  ├─ L2: Redis (shared, multi-orchestrator)
│  ├─ L3: PostgreSQL (persistent, auditable)
│  └─ L4: Disk (crash recovery fallback)
├─ Can execute inline async tasks (in same process)
├─ Can delegate to Teams/Roles (spawn subprocess)
│  ├─ Team runs in isolated subprocess
│  ├─ Team has own PID, memory, event loop
│  ├─ Team contains TeamLeader + Workers/TeamMembers
│  ├─ Team shares cache via Redis/PostgreSQL
│  ├─ Team must report results back via IPC
│  └─ Communication: Pipe or socket
└─ Role: Orchestrator (primary execution)
```

**See `.plan/architecture/caching-and-memory.md` for full caching strategy**

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
