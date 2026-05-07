## 🔐 SESSION RUN MODES & PERMISSIONS

> **Path convention** (applies to ALL modes below):
> - Session working dir: `~/.css/sessions/session-<sid>/`
> - Project source dir: resolved via `ProjectManager.get(project_id).source_dir` (e.g. `/home/user/my-project/`)
> - No `.css/` folders inside project source trees

---

### Development Mode (Up to 3 Separate Processes)
```
Session [mode=development]

Process 1 (PID: 1001): Planner Orchestrator
├─ Role: Planner
├─ Permissions (Read-Only Code + Limited Write)
│  ├─ Read: project.source_dir  (project code, config)
│  ├─ Write: ~/.css/sessions/<sid>/plan/  only
│  ├─ Permission model: Code analysis, no modifications
│  └─ Context: Planning decisions, architecture, proposals
├─ Process Isolation: Separate process
├─ Output Paths
│  ├─ Proposals: ~/.css/sessions/<sid>/plan/
│  ├─ Decisions: ~/.css/sessions/<sid>/plan/decisions/
│  └─ Analysis:  ~/.css/sessions/<sid>/plan/analysis/
└─ Use Cases
   ├─ Architectural review
   ├─ Feature design proposals
   ├─ Code audit & analysis
   └─ Implementation planning

Process 2 (PID: 1002): Main Orchestrator
├─ Role: Orchestrator
├─ Permissions (Full Project Access)
│  ├─ Read: project.source_dir (full project)
│  ├─ Write: project.source_dir (full project)
│  ├─ Permission model: Full execution capability
│  └─ Context: Implement, test, modify code
├─ Process Isolation: Separate process
├─ Output Paths
│  ├─ Code changes: project.source_dir/src/, project.source_dir/tests/
│  ├─ Test results: ~/.css/sessions/<sid>/results/
│  └─ Artifacts:   ~/.css/sessions/<sid>/artifacts/
├─ Contains:
│  ├─ Team spawning (creates TeamLeader roles)
│  ├─ Task delegation (assigns to Workers/TeamMembers)
│  └─ Result aggregation
└─ Use Cases
   ├─ Feature implementation
   ├─ Code modifications
   ├─ Testing & verification
   └─ Bug fixes

Process 3 (PID: 1003): Background Triage Orchestrator
├─ Role: Triage
├─ Permissions (Read + Limited Write)
│  ├─ Read: project.source_dir, logs
│  ├─ Write: ~/.css/sessions/<sid>/logs/ only
│  └─ Permission model: Task routing
├─ Process Isolation: Separate process (lightweight, always-on)
├─ Functions:
│  ├─ Task prioritization
│  ├─ Route to appropriate team/role
│  ├─ Background processing
│  └─ Status monitoring
└─ Use Cases
   ├─ Task prioritization
   ├─ Routing to appropriate team
   └─ Background processing
```

### Red Team Mode (2 Separate Processes)
```
Session [mode=red_team]

Process 1 (PID: 2001): Main Orchestrator (Attack Context)
├─ Role: Orchestrator
├─ Permissions: project.source_dir + system paths (per PathGrant)
├─ Process Isolation: Separate process
├─ Context: Penetration testing, vulnerability discovery
├─ Output: ~/.css/sessions/<sid>/findings/, ~/.css/sessions/<sid>/artifacts/
├─ Tasks: Simulate attacker behavior
└─ Contains: Team spawning, Worker/TeamMember delegation

Process 2 (PID: 2002): Background Triage Orchestrator
├─ Role: Triage
├─ Permissions: Read-only + write ~/.css/sessions/<sid>/logs/ only
├─ Process Isolation: Separate process
├─ Context: Task routing & prioritization
├─ Functions: Background processing
└─ Tasks: Route attack tasks, prioritize findings
```

### Blue Team Mode (2 Separate Processes)
```
Session [mode=blue_team]

Process 1 (PID: 2001): Main Orchestrator (Defense Context)
├─ Role: Orchestrator
├─ Permissions: project.source_dir + system paths (per PathGrant)
├─ Process Isolation: Separate process
├─ Context: Detection, remediation, hardening
├─ Output: ~/.css/sessions/<sid>/findings/, ~/.css/sessions/<sid>/artifacts/
├─ Tasks: Simulate defender behavior
└─ Contains: Team spawning, Worker/TeamMember delegation

Process 2 (PID: 2002): Background Triage Orchestrator
├─ Role: Triage
├─ Permissions: Read-only + write ~/.css/sessions/<sid>/logs/ only
├─ Process Isolation: Separate process
├─ Context: Task routing & prioritization
├─ Functions: Background processing
└─ Tasks: Route defense tasks, prioritize mitigations
```

### Purple Team Mode (2 Separate Processes)
```
Session [mode=purple_team]

Process 1 (PID: 2001): Red Orchestrator (Attack Context)
├─ Role: Orchestrator
├─ Permissions: Full access (per PathGrant)
├─ Process Isolation: Separate process
├─ Output: ~/.css/sessions/<sid>/findings/red/
└─ Tasks: Simulate attacker behavior

Process 2 (PID: 2002): Blue Orchestrator (Defense Context)
├─ Role: Orchestrator
├─ Permissions: Full access (per PathGrant)
├─ Process Isolation: Separate process
├─ Output: ~/.css/sessions/<sid>/findings/blue/
└─ Tasks: Simulate defender behavior

Shared Results Queue (via IPC):
├─ Red findings → Blue response queue
├─ Coordinated assessment
└─ Comprehensive security evaluation
```

### Permission Model Architecture

Permissions are managed by `@permissions` module (Phase 15). Each orchestrator process gets explicit PathGrants at session start. See `core/permissions/plan.md` for full design.

```python
# At session start, orchestrator gets PathGrants via GrantManager:
#
# Planner mode:
#   grant_path(agent_id, project.source_dir + "/**", {READ})
#   grant_path(agent_id, "~/.css/sessions/<sid>/plan/**", {READ, WRITE})
#
# Dev mode (main orchestrator):
#   grant_path(agent_id, project.source_dir + "/**", {READ, WRITE})
#   grant_path(agent_id, "~/.css/sessions/<sid>/**", {READ, WRITE})
#
# Red/Blue/Purple (system-level tools need elevated grants):
#   grant_path(agent_id, project.source_dir + "/**", {READ, WRITE})
#   grant_path(agent_id, "~/.css/sessions/<sid>/**", {READ, WRITE})
#   grant_path(agent_id, "/etc/**", {READ}, elevated=False)
#   grant_path(agent_id, "/usr/bin/nmap", {EXECUTE}, elevated=True)
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
