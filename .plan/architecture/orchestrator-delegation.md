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
├─ 3. Initialize Team Roles (in subprocess)
│     ├─ TeamLeader role
│     │  ├─ Listen on communication channel (pipe/socket)
│     │  ├─ Receive agent delegations
│     │  ├─ Coordinate Workers/TeamMembers
│     │  └─ Send results back
│     │
│     └─ Worker/TeamMember roles
│        ├─ Execute tasks
│        ├─ Run agents
│        └─ Perform actual work
│
└─ 4. Return Team object
    ├─ team_id
    ├─ process_id
    ├─ communication_channel
    ├─ team_leader_protocol
    └─ worker_roles
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

### Phase 6 Message Contract

The logical message types above should be represented as `msgspec.Struct`
contracts (`DelegateAgentMsg`, `ResultMsg`, `StatusMsg`, `HeartbeatMsg`,
`ShutdownMsg`) and transported via `msgspec.msgpack`.
This replaces untyped dict payloads while preserving the same delegation semantics.

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

### entry_points-based Agent Registry (Phase 6)

Replace path-based dynamic import as default with entry-point discovery:

1. Query `importlib.metadata.entry_points(group="css.modules")`.
2. Build registry from declared entry-point names and callables.
3. Limit team process loading to declared modules for predictable startup and test isolation.

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
