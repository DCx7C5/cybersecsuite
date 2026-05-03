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
│   ├── session-<uuid>/      # Actual sessions
│   ├── session-<uuid>/
│   └── session-<uuid>/
├── plans/                    
│   └── plan-<uuid>/         # Planner files (development mode only)
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

### Project Source Files

```markdown
src/css/
├── api_services/
│   ├── <provider>/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── response.py
│   │   └── exceptions.py
│   └── ...
├── core/
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │
│
└── modules/
    └── <module>/
        ├── __init__.py
        ├── models.py
        ├── endpoints.py
        ├── types.py
        ├── enums.py
        ├── exceptions.py
        └── other files

```


---
