# @css_a2a — Fast Internal Agent-to-Agent Communication

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Location**: `src/css/modules/css_a2a/` (currently in `google_a2a/` but should be moved)

**Responsibility**: Direct agent-to-agent communication **within CyberSecSuite** (internal protocol, NOT Google A2A).

---

## Purpose

- Enable team agent collaboration within same CyberSecSuite instance
- Fast protocol (in-process + IPC, not HTTPS)
- Task lifecycle management (SUBMITTED → WORKING → COMPLETED/FAILED)
- Team broadcasting & direct messaging
- Integration with @cache for task storage

---

## Architecture

```
Agent A (Orchestrator)
    ↓ [A2ACommunicator]
Redis MessageDispatcher (L2 cache, db=3)
    ↓
Agent B (Team Member)
    ↓
Task execution + findings storage in @cache
```

---

## Key Communication Patterns

### Pattern 1: Same-Team A2A (In-Process, Shared Context)

```
Team Subprocess
│
├─ TeamLeader (coordinator)
├─ Worker-1 (Agent-A)
├─ Worker-2 (Agent-B)  
├─ Worker-3 (Agent-C)
│
└─ Shared Context
   ├─ Knowledge Base (asyncio.Queue, thread-safe)
   ├─ Agent Registry
   ├─ Task Queue (team-local)
   └─ Result Cache

Direct A2A Communication (No Orchestrator Involved):
Agent-A → Query KB (Agent-B result)
Agent-B → Analyze Agent-A findings
Agent-C → Synthesize Agent-A + Agent-B results
```

**Implementation**:

```python
class TeamAToACommunication:
    """Enable direct agent-to-agent communication within team"""
    def __init__(self):
        self.knowledge_base = {}  # agent_id → data (shared)
        self.kb_lock = asyncio.Lock()
        self.agent_queues = {}  # agent_id → asyncio.Queue
    
    async def publish_finding(self, agent_id: str, finding_key: str, data):
        """Agent publishes finding to shared KB (A2A)"""
        async with self.kb_lock:
            self.knowledge_base[finding_key] = {
                "source_agent": agent_id,
                "data": data,
                "timestamp": now()
            }
    
    async def subscribe_finding(self, agent_id: str, finding_key: str, timeout_sec=None):
        """Agent waits for another agent's finding (direct A2A)"""
        # Poll with timeout
        start = time.time()
        while True:
            async with self.kb_lock:
                if finding_key in self.knowledge_base:
                    return self.knowledge_base[finding_key]
            
            if timeout_sec and (time.time() - start) > timeout_sec:
                raise TimeoutError(f"Finding {finding_key} not available")
            
            await asyncio.sleep(0.1)  # Backoff

class Worker:
    """Agent role: executes tasks, communicates directly with other agents"""
    def __init__(self, agent_id: str, a2a_comm: TeamAToACommunication):
        self.agent_id = agent_id
        self.a2a = a2a_comm
    
    async def run(self, params):
        """Execute task with direct A2A communication"""
        # Do work
        analysis = await self.analyze(params)
        
        # Publish to shared KB (direct A2A)
        await self.a2a.publish_finding(
            self.agent_id,
            f"analysis-{self.agent_id}",
            analysis
        )
        
        # Wait for another agent's finding (direct A2A)
        other_analysis = await self.a2a.subscribe_finding(
            self.agent_id,
            f"analysis-other-agent",
            timeout_sec=30
        )
        
        # Synthesize results (direct A2A coordination)
        final_result = await self.synthesize(analysis, other_analysis)
        return final_result
```

---

### Pattern 2: Cross-Team A2A (IPC, Message Passing)

```
Team-1 Subprocess          Team-2 Subprocess
│                          │
├─ TeamLeader-1            ├─ TeamLeader-2
├─ Worker-A                ├─ Worker-D
├─ Worker-B                ├─ Worker-E
│                          │
└─ IPC Channel (Pipe/Socket)
   Worker-A ←→ Worker-D (direct)
   Worker-B ←→ Worker-E (direct)
   
Direct A2A (No Orchestrator Involved):
Worker-A (Team-1) → send finding to Worker-D (Team-2)
Worker-D (Team-2) → receive + process
Worker-D → send response back to Worker-A
```

**Implementation**:

```python
class CrossTeamA2ACommunication:
    """Enable direct agent-to-agent communication across teams"""
    def __init__(self, team_id: str, other_teams: Dict[str, Tuple]):
        self.team_id = team_id
        self.other_teams = other_teams  # team_id → (pipe_conn, agent_id)
    
    async def send_to_agent(self, to_agent_id: str, to_team_id: str, message: dict):
        """Send message directly to agent in different team (A2A, not via Orchestrator)"""
        if to_team_id not in self.other_teams:
            raise ValueError(f"Team {to_team_id} not connected")
        
        conn, _ = self.other_teams[to_team_id]
        
        msg = {
            "type": "a2a_message",
            "from_agent": self.agent_id,
            "from_team": self.team_id,
            "to_agent": to_agent_id,
            "to_team": to_team_id,
            "payload": message,
            "timestamp": now()
        }
        
        await conn.send_async(msg)
    
    async def receive_from_agent(self, timeout_sec=None):
        """Receive direct message from agent in another team (A2A)"""
        # Listen on all IPC channels
        # Return first message received
        tasks = [
            asyncio.create_task(conn.recv_async())
            for conn, _ in self.other_teams.values()
        ]
        
        done, pending = await asyncio.wait(
            tasks,
            timeout=timeout_sec,
            return_when=asyncio.FIRST_COMPLETED
        )
        
        if done:
            msg = done.pop().result()
            return msg
        else:
            raise TimeoutError("No A2A message received")

class Worker:
    def __init__(self, agent_id: str, a2a_cross: CrossTeamA2ACommunication):
        self.agent_id = agent_id
        self.a2a_cross = a2a_cross
    
    async def run(self, params):
        """Execute with cross-team A2A communication"""
        # Do work
        findings = await self.analyze(params)
        
        # Send directly to agent in Team-2 (A2A, no Orchestrator)
        await self.a2a_cross.send_to_agent(
            to_agent_id="analyzer-2",
            to_team_id="team-2",
            message={"findings": findings}
        )
        
        # Wait for response from Team-2 agent (direct A2A)
        response = await self.a2a_cross.receive_from_agent(timeout_sec=60)
        
        return {"original": findings, "response": response}
```

---

## Orchestrator ↔ Team Communication (Level 1)

**Roles involved:**
- **Orchestrator** (parent process) — sends delegations
- **TeamLeader** (team subprocess) — receives delegations, coordinates Workers/TeamMembers
- **Workers/TeamMembers** (team subprocess) — execute tasks

### Channel Setup

```python
import asyncio
import json
from multiprocessing import Pipe

# Main Orchestrator
parent_conn, child_conn = Pipe()

# Spawn team subprocess
team_process = subprocess.Popen(
    [sys.executable, "-m", "css.orchestration.team_leader"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    pass_fds=(child_conn.fileno(),)
)

# Team Leader (in subprocess, receives child_conn)
async def team_leader_main(conn):
    while True:
        msg = await read_message(conn)
        await handle_delegation(msg)
        result = await execute_result()
        await write_message(conn, result)
```

### Message Protocol (JSON-RPC Style)

```json
// Orchestrator → Team: DELEGATE
{
  "id": "msg-001",
  "type": "delegate_agent",
  "agent_type": "forensic_analyzer",
  "agent_version": "3",
  "params": {
    "target": "/tmp/suspicious.log",
    "mode": "aggressive"
  },
  "delegation_mode": "async",
  "callback_id": "task-123",
  "timeout_sec": 300,
  "timestamp": "2026-05-03T13:45:00Z"
}

// Team → Orchestrator: RESULT
{
  "id": "msg-001",
  "type": "result",
  "callback_id": "task-123",
  "agent_type": "forensic_analyzer",
  "status": "success",
  "result": {
    "findings": [...],
    "risk_score": 8.5,
    "timeline": {...}
  },
  "execution_time_sec": 45.3,
  "timestamp": "2026-05-03T13:45:45Z"
}
```

### Sync vs Async Delegation Modes

```python
# MODE 1: ASYNC (Fire & Forget)
# Orchestrator sends delegation, doesn't wait for result
message = {
    "type": "delegate_agent",
    "delegation_mode": "async",
    "callback_id": "task-123"
}
await conn.send(message)
# Continue immediately, result comes later via separate message

# MODE 2: SYNC (Wait for Result)
# Orchestrator sends delegation, waits for response with timeout
message = {
    "type": "delegate_agent",
    "delegation_mode": "sync",
    "callback_id": "task-123",
    "timeout_sec": 60
}
await conn.send(message)
result = await asyncio.wait_for(conn.recv(), timeout=60)
# Blocks until result received or timeout
```

### Callback Correlation

```python
# Main Orchestrator maintains callback registry
class OrchestratorCallbackRegistry:
    def __init__(self):
        self.pending_callbacks = {}  # callback_id → Future
    
    async def delegate_async(self, agent_type, params):
        callback_id = generate_uuid()
        future = asyncio.Future()
        self.pending_callbacks[callback_id] = future
        
        msg = {
            "type": "delegate_agent",
            "callback_id": callback_id,
            "agent_type": agent_type,
            "params": params,
            "delegation_mode": "async"
        }
        await self.team_conn.send(msg)
        return callback_id  # Return immediately
    
    async def handle_result_message(self, msg):
        callback_id = msg["callback_id"]
        future = self.pending_callbacks.pop(callback_id)
        future.set_result(msg["result"])  # Wake up waiter

# Later, when result arrives:
result = await registry.pending_callbacks[callback_id]  # Blocks until result
```

---

## Team Leader ↔ Agents Communication (Level 2)

**Roles involved:**
- **TeamLeader** (subprocess coordinator) — manages task distribution
- **Workers/TeamMembers** (subprocess executors) — run agents, perform tasks

### Same-Process Async Coordination

```python
class TeamLeader:
    """TeamLeader role: coordinates Workers/TeamMembers in subprocess"""
    def __init__(self):
        self.agents = {}  # agent_id → Agent instance
        self.running_tasks = {}  # task_id → asyncio.Task (Workers)
    
    async def delegate_agent(self, msg):
        """Assign work to Workers/TeamMembers"""
        agent_id = msg["agent_type"]
        agent = self.agents.get(agent_id)
        
        if not agent:
            agent = self.hotload_agent(agent_id)
            self.agents[agent_id] = agent
        
        # Run agent as Worker/TeamMember asynchronously
        task = asyncio.create_task(
            agent.run(msg["params"])
        )
        self.running_tasks[msg["callback_id"]] = task
        
        return {"status": "started", "callback_id": msg["callback_id"]}
```

---

## Key Classes

- `A2ACommunicator` — Per-agent interface for task management
- `A2ACommunicationGroup` — Team management (add/remove members, broadcast)
- `MessageDispatcher` — Redis pub/sub routing
- `InternalMessage` — Typed message schema (Pydantic)

---

## API

```python
a2a = A2ACommunicator(agent_id="analyst", dispatcher=dispatcher)

# Create task
task = await a2a.create_task(task_id="t1", message=a2a_message)

# Transition states
await a2a.set_working(task_id="t1")
await a2a.set_completed(task_id="t1", artifact=result)

# Team operations
group = A2ACommunicationGroup(name="forensics_team")
await group.add_member("investigator1")
await group.broadcast_task(task_id="t1", message=message)
```

---

## When to Use CSS A2A

**Use CSS A2A When:**
- ✅ Agents in same team (fast, low-latency)
- ✅ Agents across our teams (controlled, reliable)
- ✅ Internal security analysis (no external dependency)
- ✅ High-throughput communication needed
- ✅ Sensitive data (stays in-system)

---

## Implementation Checklist

- [ ] ⚠️ **Move to `src/css/modules/css_a2a/`** (currently in google_a2a folder)
  - Move `a2a_comms.py`, `dispatcher.py`, `int_comms.py` → `css_a2a/`
  - Create `css_a2a/__init__.py` with public API
  - Update imports in google_a2a to use css_a2a module
- [ ] Add integration tests
- [ ] Add telemetry/metrics
- [ ] Add logger initialization in `__init__.py`

---

## Module Pattern

```python
# src/css/modules/css_a2a/__init__.py
"""Fast internal agent-to-agent communication (NOT Google A2A)."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .a2a_comms import A2ACommunicator, A2ACommunicationGroup
from .dispatcher import MessageDispatcher

__all__ = ['A2ACommunicator', 'A2ACommunicationGroup', 'MessageDispatcher']
```

---

**Status**: ✅ Done (Implementation complete, reorganization pending) | **Last Updated**: 2026-05-03
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: See .plan/modules/module-audit-matrix.md for full audit results.
