## ⚡ PARALLELIZATION ARCHITECTURE

### Core Principle: Independent Agents (Workers/TeamMembers)

All parallelization is built on **independent Orchestrators pulling from shared queues**, delegating to **Workers/TeamMembers**, not Orchestrators pushing tasks.

```
┌─ Database (PostgreSQL) ─┐
│                         │
│  Task Queue Table       │
│  ├─ task-1 (pending)    │
│  ├─ task-2 (pending)    │
│  ├─ task-3 (pending)    │
│  └─ ...                 │
│                         │
└─────────────────────────┘
         ↑ ↑ ↑
         │ │ │
    PULL (atomic)
         │ │ │
    ┌────┴─┴─┴────┐
    │              │
 ORCH-1        ORCH-2        ORCH-3
 (Orchestrator) (Orchestrator) (Orchestrator)
 Process       Process       Process
 │ PID: 1001   │ PID: 1002   │ PID: 1003
 │ Role: Orch  │ Role: Orch  │ Role: Orch
 │             │             │
 │ Delegates to Workers/TeamMembers (in team subprocesses)
 │
 └─────────────┴─────────────┘
   [All running in parallel]
```

**Key Property**: No coordination needed between Orchestrators. Each pulls independently, delegating to Workers.

---

### Level 1: Orchestrator-Level Parallelization

#### Pattern: Pull-Based Task Distribution

```
Database Queue Pattern:
┌────────────────────────────────────────────┐
│  tasks (pending)                           │
├────────────────────────────────────────────┤
│  task-1 | pending | NULL                   │
│  task-2 | pending | NULL                   │
│  task-3 | pending | NULL                   │
│  task-4 | pending | NULL                   │
│  task-5 | pending | NULL                   │
└────────────────────────────────────────────┘

Orchestrator-1 Loop:
  1. SELECT task FROM queue WHERE status='pending' LIMIT 1 FOR UPDATE
     → Gets task-1 atomically
  2. UPDATE tasks SET status='assigned', orchestrator_id=1 WHERE id=task-1
  3. Execute task asynchronously
  4. Push result + idempotency_key
  5. UPDATE tasks SET status='completed', result=...
  6. Loop back → Pull next task

[Orchestrator-2 and -3 do the same independently]

Result: 5 tasks complete 3x faster (N tasks ÷ N orchestrators)
```

#### Guarantees

- ✅ **No duplicate execution**: FOR UPDATE lock ensures atomic pull
- ✅ **No lost tasks**: Failed pull rolls back automatically
- ✅ **Scalable**: Add more orchestrators → tasks complete faster
- ✅ **Fault tolerant**: If Orch-1 crashes, tasks reassigned to next orchestrator

---

### Level 2: Team-Based Parallelization

#### Level 2: Team-Based Parallelization

#### Pattern: Isolated Task Queues per Team (TeamLeaders coordinate Workers/TeamMembers)

```
Session
│
├─ Team-Engineering (max 5 Orchestrators delegate)
│  ├─ Queue (isolated)
│  │  ├─ eng-task-1 (pending)
│  │  ├─ eng-task-2 (pending)
│  │  └─ eng-task-3 (pending)
│  │
│  └─ Team Subprocess
│     ├─ TeamLeader role (coordinator)
│     └─ Workers/TeamMembers (N agents/workers)
│        ├─ worker-1 ─→ pulls from Team-Eng queue
│        ├─ worker-2 ─→ pulls from Team-Eng queue
│        └─ worker-3 ─→ pulls from Team-Eng queue
│
├─ Team-Security (max 10 Orchestrators delegate)
│  ├─ Queue (isolated, separate from Team-Eng)
│  │  ├─ sec-task-1 (pending)
│  │  ├─ sec-task-2 (pending)
│  │  └─ sec-task-3 (pending)
│  │
│  └─ Team Subprocess
│     ├─ TeamLeader role (coordinator)
│     └─ Workers/TeamMembers (N agents/workers)
│        ├─ worker-1 ─→ pulls from Team-Sec queue
│        ├─ worker-2 ─→ pulls from Team-Sec queue
│        └─ ... (up to 10)
│
└─ Team-Compliance (max 1 Orchestrator delegates)
   ├─ Queue (isolated)
   │  ├─ comp-task-1 (pending)
   │  └─ comp-task-2 (pending)
   │
   └─ Team Subprocess
      ├─ TeamLeader role (coordinator)
      └─ Workers/TeamMembers (1 worker)
         └─ worker-1 ─→ pulls from Team-Comp queue

ISOLATION BENEFITS:
✅ Team-Eng Workers execute in parallel (up to 5 tasks)
✅ Team-Sec Workers execute independently (up to 10 tasks)
✅ Total: UP TO 16 TASKS RUNNING IN PARALLEL
✅ If Team-Eng crashes → Team-Sec/Team-Comp unaffected
✅ Resource quotas enforced: no team can hog all Orchestrators
```

#### Resource Quota Enforcement

```python
# Each team has a quota
class Team:
    max_concurrent_orchestrators: int = 5  # Team-Eng can spawn max 5
    orchestrator_count: int = 0            # Currently running

# When spawning orchestrator:
if orchestrator_count >= max_concurrent_orchestrators:
    raise QuotaExceeded(f"Team {team.name} already has {max_concurrent_orchestrators} orch")

# Result: Team-Eng ≤ 5 orch, Team-Sec ≤ 10 orch, no contention
```

---

### Level 3: Agent-Level Parallelization (Within Team)

#### Pattern: Async Delegation + Concurrent Task Execution

```
Main Orchestrator (Session)
│
├─ Task: "Analyze 3 files"
│
└─ Strategy: Delegate to Team with 3 agents running in parallel
   
   Team (Subprocess)
   │
   ├─ Team Leader (coordinator)
   │  │
   │  ├─ Delegate: Agent-Analyzer-1 (async)
   │  │  └─ → Analyze file-1 (long-running)
   │  │
   │  ├─ Delegate: Agent-Analyzer-2 (async)
   │  │  └─ → Analyze file-2 (long-running)
   │  │
   │  └─ Delegate: Agent-Analyzer-3 (async)
   │     └─ → Analyze file-3 (long-running)
   │
   └─ [All 3 agents running concurrently in team subprocess]
      ├─ Agent-1 result ready (2s) → process
      ├─ Agent-2 result ready (3s) → process
      └─ Agent-3 result ready (2.5s) → process
      
      Total time: ~3s (max of 3), not 7.5s (sum of 3)
```

#### Concurrency Control

```python
class Team:
    async def delegate_agents_concurrent(self, agents: List[Agent]) -> List[Result]:
        """Run multiple agents in parallel"""
        tasks = [
            asyncio.create_task(self.run_agent(agent))
            for agent in agents
        ]
        return await asyncio.gather(*tasks)

# Usage:
results = await team.delegate_agents_concurrent([
    Agent("analyzer", file="file-1"),
    Agent("analyzer", file="file-2"),
    Agent("analyzer", file="file-3"),
])
# All 3 agents run concurrently, wait for all to finish
```

---

### Level 4: Mode-Based Parallelization

#### Development Mode: Dual Orchestrators (Parallel Planning + Execution)

```
Session [mode=development]
│
├─ Orchestrator (Planner role) (Process 1)
│  ├─ Reads project.source_dir
│  ├─ Generates proposals (async)
│  ├─ Writes to ~/.css/sessions/<sid>/plan/ (isolated)
│  └─ [Running in parallel with Orch-Dev]
│
├─ Orchestrator (Orchestrator role) (Process 2)
│  ├─ Reads decisions from plan
│  ├─ Executes implementation (async)
│  ├─ Delegates to Workers/TeamMembers
│  ├─ Writes to project.source_dir/src/, results to ~/.css/sessions/<sid>/results/
│  └─ [Running in parallel with Orch-Plan]
│
└─ Orchestrator (Triage role) (Process 3, background)
   ├─ Routes tasks (lightweight)
   └─ [Running asynchronously]

TIMELINE:
Time 0s: All 3 orchestrators start (separate processes)
Time 0-5s: Planner analyzes architecture
Time 1-6s: Orchestrator implements feature (parallel)
Time 2-4s: Triage routes tasks
Time 6s: All finish, results merged

Result: 6s total (vs 12s if serial)
```

#### Red/Blue/Purple Modes: Coordinated Parallel Attacks/Defenses

```
Session [mode=purple_team]
│
├─ Orchestrator (Orchestrator role - Red) (Process 1)
│  ├─ Spawn N attack workers (parallel)
│  ├─ Exploit vulnerabilities simultaneously
│  └─ Report findings
│
├─ Orchestrator (Orchestrator role - Blue) (Process 2)
│  ├─ Spawn N defense workers (parallel)
│  ├─ Implement patches simultaneously
│  └─ Report mitigations
│
└─ Shared Results Queue (coordination)
   ├─ Red findings → Blue response
   └─ Comprehensive assessment

TIMELINE:
Red attacks (parallel): 5s
Blue defends (parallel): 5s
Assessment: 10s (coordinated)

Result: Both orchestrators fully utilized, parallel execution
```

---

### Parallelization Guarantees

#### 1. Atomicity (No Duplicate Execution)
```sql
-- Task pull is atomic (database level)
BEGIN TRANSACTION;
SELECT task_id FROM tasks WHERE status='pending' LIMIT 1 FOR UPDATE;
UPDATE tasks SET status='assigned', orchestrator_id=? WHERE task_id=?;
COMMIT;

-- Idempotency key prevents re-execution even if retry
UNIQUE(idempotency_key) ensures each result only recorded once
```

#### 2. Isolation (Teams Don't Interfere)
```
Team-A queue (isolated DB)
├─ 100 tasks for Team-A
└─ Orch-A1, Orch-A2, ... (pull from Team-A queue only)

Team-B queue (separate DB)
├─ 100 tasks for Team-B
└─ Orch-B1, Orch-B2, ... (pull from Team-B queue only)

If Team-A's DB goes down → Team-B unaffected
```

#### 3. Fairness (Resource Quotas)
```python
# Each team has max concurrent orchestrators
Team-A: max_concurrent = 3  → Can spawn max 3 processes
Team-B: max_concurrent = 10 → Can spawn max 10 processes

# Enforced at spawn time (not run time)
If Team-A tries to spawn 4th orch → Blocked (quota exceeded)
```

#### 4. Fault Tolerance (Crash Recovery)
```
Orchestrator-1 (Process PID 1001) crashes
│
├─ Heartbeat monitor detects: heartbeat_at < now() - 300s
├─ Set status = "crashed"
├─ Reassign all tasks: assigned_to=orch-1 → status='pending'
├─ Spawn replacement orchestrator
└─ Replacement pulls reassigned tasks

Result: No tasks lost, no duplicate execution (idempotency keys)
```

---

### Performance Model

#### Speedup Formula
```
Serial Time:     T_serial = sum(t_1 + t_2 + ... + t_N)
Parallel Time:   T_parallel = max(t_1, t_2, ..., t_N) [with N orchestrators]

Speedup = T_serial / T_parallel ≤ N (Amdahl's Law)

Example (5 tasks, each 10s):
Serial:    50s
Parallel (1 orch): 50s
Parallel (2 orch): 25s (speedup: 2x)
Parallel (5 orch): 10s (speedup: 5x)
Parallel (10 orch): 10s (speedup: 5x, diminishing returns)
```

#### Contention & Overhead
```
Low Contention (few tasks per orch):
└─ Near-linear speedup (close to N x faster)

High Contention (shared resources):
├─ Database locks (task queue)
├─ Network I/O (coordination)
└─ Reduced speedup (sublinear)

Mitigation: Use pull-based model (lock-free), separate queues per team
```

---

### Example: Multi-Team Forensic Investigation (Parallel)

```
Main Orchestrator (Session)
├─ Task: "Full forensic analysis of system"
├─ Strategy: Create 3 teams, each analyzing in parallel
│
├─ Team-1: Process Analysis (max 2 orch)
│  ├─ Orch-1a: Analyze process tree (2s)
│  └─ Orch-1b: Extract process memory (3s)
│     └─ → Results ready at 3s (parallel execution)
│
├─ Team-2: Network Analysis (max 2 orch)
│  ├─ Orch-2a: Analyze network connections (2s)
│  └─ Orch-2b: Analyze DNS queries (2s)
│     └─ → Results ready at 2s (parallel execution)
│
├─ Team-3: Memory Forensics (max 1 orch)
│  └─ Orch-3a: Dump and analyze memory (5s)
│     └─ → Results ready at 5s
│
└─ Aggregation
   ├─ Wait for all 3 teams (max of 5s, 3s, 2s = 5s)
   └─ Generate final report (1s)
   
TIMELINE:
- Serial:  2+3+2+2+5+1 = 15s
- Parallel (Team-1 + Team-2 + Team-3): max(3s, 2s, 5s) + 1s = 6s
- Speedup: 15s / 6s = 2.5x faster
```

---

### Key Takeaways

1. **Pull-based model** (not push) ensures no central bottleneck
2. **Team isolation** prevents resource contention between teams
3. **Resource quotas** prevent runaway resource consumption
4. **Async delegation** enables sub-process concurrency
5. **Fault tolerance** with idempotency keys ensures correctness
6. **Near-linear speedup** with N orchestrators (up to practical limits)

---
