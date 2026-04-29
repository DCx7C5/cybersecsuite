# Hierarchical Scope Architecture (Phase 5A — Corrected)

A filesystem-based five-level scope hierarchy for managing permissions, data access, and state isolation across CyberSecSuite. Each scope level corresponds to a directory hierarchy with specific read/write permissions, backed by database models in Tortoise ORM.

## Architecture Overview: Filesystem Hierarchy

```
~/.claude/                                       GLOBAL SCOPE (read-only)
  └─ config/, cache/, shared/

~/.cybersecsuite/                                APP SCOPE (read-write)
  └─ config/, cache/, plugins/

$(pwd)/.css/                                     PROJECT SCOPE (read-write)
  ├─ .claiverc
  ├─ index/
  └─ runtime-<rid>/
     ├─ config.json
     ├─ cache/
     └─ worktree-<sid>/                         SESSION SCOPE (read-write, multiple)
        ├─ config.json
        ├─ state.json
        └─ cache/, scratch/
```

---

## Scope Levels (5 + Database Integration)

### Level 1: Global Scope

**Filesystem Location**: `~/.claude/` (read-only)  
**Reachable**: After Claude/Copilot installation  
**Database Model**: `Application` (app-level metadata)

**What Lives Here**:
- System configuration (immutable)
- Shared cache: compiled patterns, templates, indexed data
- Global plugins (system-managed)

**Permissions**:
- Read: All processes
- Write: System installer only
- Visibility: Global

**Filesystem Examples**:
```
~/.claude/
├── config/core.json            (immutable system config)
├── cache/patterns/             (compiled prompt templates)
└── shared/constants.json       (global feature flags)
```

**Database Link**:
```python
# src/db/models/scope.py → Application model
class Application(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=256, unique=True)      # e.g., "claude"
    description = fields.TextField(default="")
    path = fields.CharField(max_length=1024, default="")      # ~/.claude/
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
```

---

### Level 2: App Scope

**Filesystem Location**: `~/.cybersecsuite/` (read-write)  
**Reachable**: After CyberSecSuite installation  
**Database Model**: `Application` + `ScopedEntry` (scope_level='app')

**What Lives Here**:
- Application configuration: user preferences, API keys, auth tokens
- Application cache: downloaded models, compiled regex, user data
- User plugins: custom extensions (user-managed)

**Permissions**:
- Read: All CyberSecSuite processes
- Write: CyberSecSuite processes (user context)
- Visibility: User-scoped

**Filesystem Examples**:
```
~/.cybersecsuite/
├── config/auth.json            (API keys, tokens)
├── config/preferences.json     (user settings)
├── cache/models/               (downloaded LLMs, embeddings)
└── plugins/                    (user custom extensions)
```

**Database Link**:
```python
# ScopedEntry with scope_level='app'
class ScopedEntry(Model):
    scope_level = fields.CharField(max_length=16, default="app")  # ← Set to 'app'
    # Applies to: preferences, API keys, user settings
```

---

### Level 3: Project Scope

**Filesystem Location**: `$(pwd)/.css/` (read-write)  
**Reachable**: After `cybersecsuite init` in project directory  
**Database Model**: `Project` + `ScopedEntry` (scope_level='project')

**What Lives Here**:
- Project configuration: `.claiverc`, build settings, project-specific plugins
- Project index: codebase index, type stubs, dependency cache
- Project cache: build artifacts, compiled outputs

**Permissions**:
- Read: All processes in project
- Write: CyberSecSuite processes in project context
- Visibility: Project-scoped

**Filesystem Examples**:
```
$(pwd)/.css/
├── .claiverc                   (project config: settings.json, rules, etc.)
├── index/
│   ├── codebase.json          (AST index of all source files)
│   ├── types.json             (extracted type definitions)
│   └── dependencies.json      (resolved dep graph)
└── cache/
    ├── build-artifacts/
    └── compiled-rules/
```

**Database Link**:
```python
# src/db/models/scope.py → Project model
class Project(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=256, unique=True)
    description = fields.TextField(default="")
    path = fields.CharField(max_length=1024, default="")      # $(pwd)/
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

# ScopedEntry with scope_level='project'
class ScopedEntry(Model):
    project = fields.ForeignKeyField("models.Project", ...)   # ← Links to Project
    scope_level = fields.CharField(max_length=16, default="project")
```

---

### Level 4: Runtime Scope

**Filesystem Location**: `$(pwd)/.css/runtime-<rid>/` (read-write)  
**Reachable**: During execution (one per agent/process)  
**Database Model**: `ScopedEntry` (scope_level='runtime', runtime_id set)

**What Lives Here**:
- Runtime configuration: execution parameters, model selection, tier routing
- Runtime cache: LLM responses, token counts, cost tracking
- Session list: index of active worktrees/sessions

**Permissions**:
- Read: Processes in this runtime
- Write: Owning process only
- Visibility: Runtime-scoped (not visible outside `runtime-<rid>/`)

**Filesystem Examples**:
```
$(pwd)/.css/runtime-abc123/
├── config.json                (execution config, model selection, tiers)
├── cache/
│   ├── llm-responses/         (cached completions)
│   ├── token-counts.json      (usage tracking)
│   └── cost-tracker.json      (billing data)
└── worktree-<sid>/            (multiple sessions per runtime)
```

**Database Link**:
```python
# ScopedEntry with scope_level='runtime'
class ScopedEntry(Model):
    scope_level = fields.CharField(max_length=16, default="runtime")  # ← 'runtime'
    runtime_id = fields.CharField(max_length=64, null=True, db_index=True)  # ← 'abc123'
    # Applies to: LLM responses, token tracking, cost data
```

**Runtime ID (`<rid>`)**: Generated at agent startup (UUID or hash of process identity)

---

### Level 5: Session Scope

**Filesystem Location**: `$(pwd)/.css/runtime-<rid>/worktree-<sid>/` (read-write, multiple)  
**Reachable**: Per worktree/session (temporary)  
**Database Models**: `Session` + `LlmSession` + `ScopedEntry` (scope_level='session')

**What Lives Here**:
- Session configuration: execution plan, breakpoints, test results
- Session state: variables, scope context, execution history
- Scratch space: temporary files, working directory

**Permissions**:
- Read: Processes in this session
- Write: Owning session process only
- Visibility: Session-scoped (isolated per worktree)

**Filesystem Examples**:
```
$(pwd)/.css/runtime-abc123/worktree-xyz789/
├── config.json                (execution plan, task definition)
├── state.json                 (variables, context, breakpoints)
├── execution-log.json         (history of operations)
├── cache/
│   ├── test-results/          (pytest output, screenshots)
│   └── artifacts/             (generated files)
└── scratch/                   (temp files, working area)
```

**Database Link**:
```python
# src/db/models/scope.py → Session model (forensic root)
class Session(Model):
    project = fields.ForeignKeyField("models.Project", ...)
    session_id = fields.CharField(max_length=128, unique=True, db_index=True)  # ← 'xyz789'
    sdk_session_id = fields.CharField(max_length=128, null=True)
    name = fields.CharField(max_length=256, default="")
    path = fields.CharField(max_length=1024, default="")      # $(pwd)/.css/runtime-abc123/worktree-xyz789/
    agent = fields.CharField(max_length=128, default="")      # Agent type
    mode = fields.CharEnumField(RedBlueMode, default=RedBlueMode.BLUE)  # blue/red/purple
    phase = fields.CharField(max_length=64, default="init")
    is_active = fields.BooleanField(default=True)
    started_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

# src/db/models/llm_session.py → LlmSession model (cost tracking)
class LlmSession(Model):
    sid = fields.CharField(max_length=12, pk=True)             # ← Hex of session_id
    repo_root = fields.CharField(max_length=512, default="")
    branch = fields.CharField(max_length=256, default="")
    opened_at = fields.DatetimeField()
    closed_at = fields.DatetimeField(null=True)
    total_input_tokens = fields.BigIntField(default=0)
    total_output_tokens = fields.BigIntField(default=0)
    total_cost_usd = fields.DecimalField(max_digits=14, decimal_places=8)
    total_calls = fields.IntField(default=0)

# ScopedEntry with scope_level='session'
class ScopedEntry(Model):
    session = fields.ForeignKeyField("models.Session", ...)    # ← Links to Session
    scope_level = fields.CharField(max_length=16, default="session")  # ← 'session'
    worktree_path = fields.CharField(max_length=1024, null=True)  # ← $(pwd)/.css/runtime-abc123/worktree-xyz789/
```

**Session ID (`<sid>`)**: Generated per worktree (12-char hex or UUID)

---

## Data Flow & Permission Model

### Scope Access Rules

```python
# Pseudo-code for scope permission checking
def can_access(user_context, scope_level, resource):
    """
    Determine if user can read/write in scope.
    
    Read permissions:
      - Global: all authenticated users (cascade down)
      - App: user processes
      - Project: project members
      - Runtime: processes in runtime
      - Session: session-owning process
    
    Write permissions:
      - Global: system only
      - App: user processes
      - Project: project maintainers
      - Runtime: runtime-owning process
      - Session: session-owning process
    """
    if scope_level == "global":
        return user_context.is_authenticated  # Read-only
    elif scope_level == "app":
        return user_context.owns_app_context
    elif scope_level == "project":
        return resource.project in user_context.projects
    elif scope_level == "runtime":
        return resource.runtime_id == user_context.current_runtime
    elif scope_level == "session":
        return resource.session == user_context.current_session
    return False
```

### Scope Inheritance Chain

```
Global (immutable config)
  ↓ (inherits read access)
App (user preferences)
  ↓ (inherits read access)
Project (project config)
  ↓ (inherits read access)
Runtime (execution context)
  ↓ (inherits read access)
Session (execution state)
```

---

## Database Model Integration

### ScopedEntry: Universal Scope Anchor

```python
# All scoped data extends ScopedEntry
class ScopedEntry(Model):
    """Abstract base for all scoped data (T045 scope_v2)."""
    
    # Scope references
    project = fields.ForeignKeyField("models.Project", null=True, on_delete=CASCADE)
    session = fields.ForeignKeyField("models.Session", null=True, on_delete=CASCADE)
    
    # 5-level scope columns (filesystem-backed)
    runtime_id = fields.CharField(max_length=64, null=True, db_index=True)  # runtime-<rid>
    worktree_path = fields.CharField(max_length=1024, null=True)             # Full path
    scope_level = fields.CharField(max_length=16, default="session")         # Level name
    
    # Lifecycle
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_active = fields.BooleanField(default=True, db_index=True)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True

# Example: Investigation extends ScopedEntry
class Investigation(ScopedEntry):
    """Forensic investigation scoped to project/session."""
    name = fields.CharField(max_length=256)
    # Inherits: project, session, runtime_id, worktree_path, scope_level
```

### Worker Context: Session-Aware Tracking

```python
# src/db/models/worker_context.py
class WorkerContext(Model):
    """Session-scoped background worker state and context tracking."""
    
    # Session reference
    session = fields.ForeignKeyField(
        "models.Session",
        related_name="worker_contexts",
        on_delete=CASCADE
    )
    
    # Worker identification
    worker_id = fields.CharField(max_length=128, db_index=True)
    worker_type = fields.CharField(max_length=64)  # 'forensic_processor', etc.
    
    # Task state
    active_task_count = fields.IntField(default=0)
    active_task_ids = fields.JSONField(default=list)
    
    # Queue state
    queue_depth = fields.IntField(default=0)
    pending_task_ids = fields.JSONField(default=list)
    
    # Error tracking
    error_count = fields.IntField(default=0)
    consecutive_errors = fields.IntField(default=0)
    last_error = fields.CharField(max_length=512, default="")
    
    # Context awareness
    recently_accessed_files = fields.JSONField(default=list)
    recently_accessed_functions = fields.JSONField(default=list)
    
    # Health and TTL
    is_active = fields.BooleanField(default=True)
    health_status = fields.CharField(max_length=16, choices=[...])
    expires_at = fields.DatetimeField(null=True)  # Auto-cleanup TTL
```

---

## Implementation: Scope Path Resolution

### Resolve Scope from Filesystem

```python
def resolve_scope_path(scope_level: str, context: Dict) -> str:
    """
    Resolve filesystem path for scope level.
    
    Args:
        scope_level: 'global', 'app', 'project', 'runtime', 'session'
        context: {
            'project_root': '/path/to/project',
            'runtime_id': 'abc123',
            'session_id': 'xyz789'
        }
    
    Returns:
        Resolved filesystem path
    """
    if scope_level == "global":
        return os.path.expanduser("~/.claude")
    
    elif scope_level == "app":
        return os.path.expanduser("~/.cybersecsuite")
    
    elif scope_level == "project":
        return os.path.join(context["project_root"], ".css")
    
    elif scope_level == "runtime":
        return os.path.join(
            context["project_root"],
            ".css",
            f"runtime-{context['runtime_id']}"
        )
    
    elif scope_level == "session":
        return os.path.join(
            context["project_root"],
            ".css",
            f"runtime-{context['runtime_id']}",
            f"worktree-{context['session_id']}"
        )
    
    raise ValueError(f"Unknown scope level: {scope_level}")
```

### Load Scope Configuration

```python
async def load_scope_config(scope_level: str, context: Dict) -> Dict:
    """
    Load configuration for scope level from filesystem + database.
    
    Cascades: session → runtime → project → app → global
    """
    scope_path = resolve_scope_path(scope_level, context)
    config_file = os.path.join(scope_path, "config.json")
    
    # Read from filesystem
    if os.path.exists(config_file):
        with open(config_file) as f:
            config = json.load(f)
    else:
        config = {}
    
    # Augment with database metadata
    if scope_level == "project":
        project = await Project.get(path=scope_path)
        config["project_id"] = project.id
        config["project_name"] = project.name
    
    elif scope_level == "session":
        session = await Session.get(path=scope_path)
        config["session_id"] = session.session_id
        config["agent"] = session.agent
        config["mode"] = session.mode
    
    return config
```

---

## Security & Isolation

### Scope-Based Access Control (RBAC)

```python
async def check_scope_permission(
    user: User,
    scope_level: str,
    action: str,  # 'read' | 'write'
    resource_id: str
) -> bool:
    """
    Check if user can perform action on resource in scope.
    """
    
    if action == "read":
        # Read cascades down from higher scopes
        if scope_level == "global":
            return user.is_authenticated
        elif scope_level == "app":
            return user.owns_app_context()
        elif scope_level == "project":
            resource = await ScopedEntry.get(id=resource_id)
            return resource.project in user.projects
        elif scope_level in ["runtime", "session"]:
            resource = await ScopedEntry.get(id=resource_id)
            return resource.session.user == user
    
    elif action == "write":
        # Write requires ownership at that scope
        if scope_level == "global":
            return user.is_system_admin()
        elif scope_level == "app":
            return user.owns_app_context()
        elif scope_level == "project":
            resource = await ScopedEntry.get(id=resource_id)
            return resource.project.maintainer == user
        elif scope_level == "runtime":
            resource = await ScopedEntry.get(id=resource_id)
            return resource.runtime_id == user.current_runtime
        elif scope_level == "session":
            resource = await ScopedEntry.get(id=resource_id)
            return resource.session == user.current_session
    
    return False
```

### Data Isolation

- **Global**: Immutable, read-only, shared across all users
- **App**: User-isolated, invisible to other users
- **Project**: Project-isolated, visible to project members
- **Runtime**: Runtime-isolated, visible only to processes in runtime
- **Session**: Session-isolated, visible only to owning process

---

## Next Steps (Phase 5B+)

1. **Implement scope enforcement middleware** in FastAPI
2. **Add scope validation** to all ScopedEntry subclasses
3. **Implement scope-based cache invalidation**
4. **Add audit logging** for scope boundary crossings
5. **Build scope-aware worker context** (WorkerContext integration)

---

**Status**: ✅ Filesystem-based scope hierarchy implemented  
**Database Integration**: ✅ Complete (Project, Session, ScopedEntry, WorkerContext)  
**Next Phase**: Phase 5B — Scope enforcement and permission checking
