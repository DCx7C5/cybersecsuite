## 🔄 FEATURE 1: MULTI-ORCHESTRATOR ARCHITECTURE

### Problem → Solution
```
PROBLEM:  1 orchestrator per session → Serial execution (slow)
SOLUTION: N orchestrators per session → Parallel execution (fast)
          Each orchestrator in separate process
```

### Process Structure

**Key Principle**: ALL orchestrators are separate processes.

```
Session Spawn
│
├─ Main Process (Session Manager)
│  ├─ Spawns Orchestrator Processes (separate)
│  ├─ Manages process lifecycle
│  ├─ Coordinates via IPC channels
│  └─ Monitors health
│
├─ Process 1 (Orchestrator)
│  ├─ PID: 1001
│  ├─ Independent event loop
│  └─ Full memory isolation
│
├─ Process 2 (Orchestrator)
│  ├─ PID: 1002
│  ├─ Independent event loop
│  └─ Full memory isolation
│
└─ Process N (Orchestrator)
   ├─ PID: 100N
   ├─ Independent event loop
   └─ Full memory isolation

Result: All processes run in parallel, never co-located
```

### Task Queue Pattern (Pull-Based)

Each orchestrator process independently pulls tasks from shared queue:

```
Database (PostgreSQL)
│
├─ Task Queue Table
│  ├─ task-1 (pending)
│  ├─ task-2 (pending)
│  ├─ task-3 (pending)
│  ├─ task-4 (pending)
│  └─ task-5 (pending)
│
└─ Orchestrator Processes (independent agents)
   │
   ├─ Orch-Process-1 (PID: 1001)
   │  ├─ [Loop]
   │  │  ├─ Check heartbeat
   │  │  ├─ Pull next task from queue (atomic)
   │  │  ├─ Execute task
   │  │  └─ Push result to result_queue
   │  └─ [Repeat]
   │
   ├─ Orch-Process-2 (PID: 1002)
   │  ├─ [Same independent loop]
   │  └─ [Repeat]
   │
   └─ Orch-Process-3 (PID: 1003)
      ├─ [Same independent loop]
      └─ [Repeat]

Result: All 5 tasks executed in parallel across 3 separate processes
```

### Orchestrator Lifecycle (Per Process)

```
1. SPAWN
   ├─ Parent spawns new process
   ├─ Create orchestrator record in DB
   ├─ Assign UUID, PID, session_id, team_id
   ├─ Child process initializes
   ├─ Set status = "active"
   └─ Start heartbeat (in child process)

2. RUNNING (In Child Process)
   ├─ Own event loop (asyncio)
   ├─ Pull task from queue (atomic)
   ├─ Execute (async)
   ├─ Push result + idempotency_key
   ├─ Update heartbeat every 5s
   ├─ Repeat

3. CRASH DETECTION (Parent monitors)
   ├─ Monitor: heartbeat_at < now() - 300s
   ├─ Set status = "crashed"
   ├─ Reassign tasks: assigned_to=orch_id → pending
   ├─ Alert team/session

4. RECOVERY
   ├─ Spawn replacement process
   ├─ Old tasks become pending (pullable by new process)
   ├─ Idempotency keys prevent re-execution

5. SHUTDOWN (Graceful, in Child Process)
   ├─ Set status = "shutting_down"
   ├─ Wait for current task to complete
   ├─ Push final result
   ├─ Set status = "inactive"
   └─ Exit process
```

### Process Isolation Guarantees

- ✅ **Memory Isolation**: Each process has own memory space (no shared state)
- ✅ **Event Loop Isolation**: Each process has own asyncio event loop
- ✅ **File Descriptor Isolation**: Separate I/O context
- ✅ **Crash Isolation**: Crash in one process ≠ crash in others
- ✅ **Atomic Task Pull**: Database lock prevents duplicate task assignment

---
