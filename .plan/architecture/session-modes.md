## 🔐 SESSION RUN MODES & PERMISSIONS

### Development Mode (Up to 3 Separate Processes)
```
SessionScope [mode=development]

Process 1 (PID: 1001): Planner Orchestrator
├─ Role: Planner
├─ Permissions (Read-Only Code + Limited Write)
│  ├─ Read: $(pwd) (project code, config)
│  ├─ Write: $(pwd)/.css/plan/ only
│  ├─ Permission model: Code analysis, no modifications
│  └─ Scope: Planning decisions, architecture, proposals
├─ Process Isolation: Separate process
├─ Output Paths
│  ├─ Proposals: $(pwd)/.css/sessions/session-<sid>/plan/
│  ├─ Decisions: $(pwd)/.css/sessions/session-<sid>/plan/decisions/
│  └─ Analysis: $(pwd)/.css/sessions/session-<sid>/plan/analysis/
└─ Use Cases
   ├─ Architectural review
   ├─ Feature design proposals
   ├─ Code audit & analysis
   └─ Implementation planning

Process 2 (PID: 1002): Main Orchestrator
├─ Role: Orchestrator
├─ Permissions (Full Project Access)
│  ├─ Read: $(pwd) (full project)
│  ├─ Write: $(pwd) (full project)
│  ├─ Permission model: Full execution capability
│  └─ Scope: Implement, test, modify code
├─ Process Isolation: Separate process
├─ Output Paths
│  ├─ Code changes: $(pwd)/src/, $(pwd)/tests/
│  ├─ Test results: $(pwd)/.css/sessions/session-<sid>/results/
│  └─ Artifacts: $(pwd)/.css/sessions/session-<sid>/
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
│  ├─ Read: $(pwd), logs
│  ├─ Write: logs only
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
SessionScope [mode=red_team]

Process 1 (PID: 2001): Main Orchestrator (Attack Context)
├─ Role: Orchestrator
├─ Permissions: Full project/system access
├─ Process Isolation: Separate process
├─ Scope: Penetration testing, vulnerability discovery
├─ Output: Attack vectors, exploits, findings
├─ Tasks: Simulate attacker behavior
└─ Contains: Team spawning, Worker/TeamMember delegation

Process 2 (PID: 2002): Background Triage Orchestrator
├─ Role: Triage
├─ Permissions: Read-only + limited write (logs)
├─ Process Isolation: Separate process
├─ Scope: Task routing & prioritization
├─ Functions: Background processing
└─ Tasks: Route attack tasks, prioritize findings
```

### Blue Team Mode (2 Separate Processes)
```
SessionScope [mode=blue_team]

Process 1 (PID: 2001): Main Orchestrator (Defense Context)
├─ Role: Orchestrator
├─ Permissions: Full project/system access
├─ Process Isolation: Separate process
├─ Scope: Detection, remediation, hardening
├─ Output: Defenses, patches, mitigations
├─ Tasks: Simulate defender behavior
└─ Contains: Team spawning, Worker/TeamMember delegation

Process 2 (PID: 2002): Background Triage Orchestrator
├─ Role: Triage
├─ Permissions: Read-only + limited write (logs)
├─ Process Isolation: Separate process
├─ Scope: Task routing & prioritization
├─ Functions: Background processing
└─ Tasks: Route defense tasks, prioritize mitigations
```

### Purple Team Mode (2 Separate Processes)
```
SessionScope [mode=purple_team]

Process 1 (PID: 2001): Red Orchestrator (Attack Context)
├─ Role: Orchestrator
├─ Permissions: Full access
├─ Process Isolation: Separate process
├─ Output: Attack findings
└─ Tasks: Simulate attacker behavior

Process 2 (PID: 2002): Blue Orchestrator (Defense Context)
├─ Role: Orchestrator
├─ Permissions: Full access
├─ Process Isolation: Separate process
├─ Output: Defense measures
└─ Tasks: Simulate defender behavior

Shared Results Queue (via IPC):
├─ Red findings → Blue response queue
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
