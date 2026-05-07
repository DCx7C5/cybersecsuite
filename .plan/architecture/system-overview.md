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

Process 3 (PID: 1003): Background Orchestrator (Intelligence)
├─ Model: Qwen3-0.6B / Phi4-mini (lightweight, always-on) via core/ollama/
├─ Role: Task triage, routing, quality gates, cost analysis
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

Process 2 (PID: 2002): Background Orchestrator (Intelligence)
├─ Model: Qwen3-0.6B / Phi4-mini (lightweight, always-on) via core/ollama/
├─ Role: Task triage, routing, quality gates
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

Each orchestrator process integrates **`core/cache`** for:
- **Task Result Caching** (idempotency keys prevent re-execution)
- **LLM Response Caching** (reduce Claude API costs 40-60%)
- **Orchestrator Heartbeat** (Redis cache for crash detection)

```
Main Orchestrator Process
├─ Access: project.source_dir (full project, via PathGrant)
├─ Cache Layer: core/cache (multi-level backends)
│  ├─ L1: In-Memory (session-local)
│  ├─ L2: Redis (shared, multi-orchestrator)
│  └─ L3: PostgreSQL (persistent, auditable)
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

**See `core/cache/plan.md` and `.plan/architecture/sdks.md` for full caching strategy**

### Session & Working Directory Layout

```
~/.css/                          # Global CSS home
├── projects/                    # ProjectManager registry
│   └── <project-id>/metadata.json  # {id, name, source_dir, created_at}
└── sessions/                    # ALL sessions live here
    └── session-<sid>/           # Default workspace (always write)
        ├── metadata.json        # {id, mode, project_id|null, agent_id, target}
        ├── plan/                # Planner mode output (dev mode only)
        ├── teams/               # Team subdivisions
        │   └── team-<name>/
        │       ├── queue.db     # SQLite task queue
        │       ├── orchestrators/
        │       └── results/
        ├── findings/            # Cybersec evidence
        ├── artifacts/           # Tool output
        ├── results/             # Aggregated results
        └── logs/

# WorkspaceRegistry (core/workspace/) — per entity (session or agent)
# Each entity holds a list of WorkspaceDirHandle entries:
#
#   workspaces[0]  = DEFAULT  ~/.css/sessions/<sid>/        READ+WRITE (always)
#   workspaces[1]  = PROJECT  /home/user/my-app/            READ+WRITE (default)
#   workspaces[N]  = EXTRA    /any/path/in/the/system       READ+WRITE (expandable)
#
# workspaces.default → workspaces[0]
# workspaces.add(path, permissions=READ|WRITE) → new WorkspaceDirHandle
# Each handle enforces its PermissionSet on all path operations.
```

**Teams, Tasks, OrchestratorPool** are still session-scoped (inside default workspace) — only the location of the session dir changed (centralized, not per-project).

### Result
- **Before**: Serial execution, 1 task at a time
- **After**: N tasks in parallel, organized by teams, fault-isolated

---

## Phase 6 Alignment (2026-05-07)

### Protocol-first runtime typing

- Runtime value objects should be modeled with `msgspec.Struct` (immutable by default).
- Contract boundaries should prefer protocol/interface behavior over inheritance-heavy base classes.

### IPC + pipeline direction

- Orchestrator/team IPC should move to `msgspec.msgpack` payloads for typed binary transport.
- Execution flow is evolving toward composable async pipeline stages (`classify → route → execute → observe`).

### CQRS/Event Store direction

- Domain mutations are tracked as immutable domain events.
- Event persistence + replay is the system-level source for forensic/audit reconstruction.
- OTEL/OpenObserve spans should be derived from domain event flow, not ad-hoc log-only instrumentation.
