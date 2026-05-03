# @permissions — Permission Management & Access Control

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Location**: `src/css/modules/permissions/`

**Responsibility**: Role-based access control, scope-based permissions, and permission enforcement.

---

## Current State

🟡 **Skeleton** (method signatures with docstrings, bodies marked `pass`)

---

## Purpose

- Enforce role-based permissions (who can do what)
- Enforce scope-based permissions (scope hierarchy)
- Provide permission checking decorators
- Manage role assignments
- Audit permission checks

---

## Implementation Checklist

- [ ] Permission checker implementation
- [ ] Role-to-permission mapping
- [ ] Scope permission resolution
- [ ] Permission enforcement decorators
- [ ] Permission audit logging
- [ ] Add logger initialization in `__init__.py`

---

## Module Pattern

```python
# src/css/modules/permissions/__init__.py
"""Permission management and access control."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .manager import PermissionManager

__all__ = ['PermissionManager']
```

---

**Status**: 🔴 Priority (Critical) | **Last Updated**: 2026-05-03
# @permissions

**Location**: [`src/css/modules/permissions/`](/home/daen/Projects/cybersecsuite/src/css/modules/permissions/)

**Responsibility**: Permission enforcement, role-based access control (RBAC), scope management, token validation, and policy checking across all CyberSecSuite modules and services.

---

## Purpose

- Manage **dual permission model**: Path permissions (r/w/x) + Tool permissions (use/not-use)
- Enforce **role-based access control** (RBAC) across 6 orchestration roles
- Implement **scope hierarchy** (GLOBAL → APP → PROJECT → RUNTIME → SESSION) with permission inheritance
- Provide **decorators, middleware, and utilities** for permission checking
- Support **multi-process and multi-team** coordination with subprocess scope isolation
- Handle **dynamic permission grants** (e.g., grant tool X to TeamLeader for Project Y at runtime)

---

## Architecture Overview

### Dual Permission Model

**Path Permissions** (File System Based):
- Unix-like model: `read`, `write`, `execute` per role per scope level
- Hierarchical inheritance: Child scope inherits parent unless explicitly restricted
- Can only **restrict**, not expand permissions from parent scope
- Enforced at filesystem level (`.plan/scopes/`)

**Tool Permissions** (Capability Based):
- Binary model: `use` or `not_use` per tool per role
- No inheritance within tool permissions themselves
- Each role has explicit tool allowlist
- Enforced at module call site (decorators, middleware)

### Role-Based Access Control (RBAC)

**6 Orchestration Roles**:

| Role | Scope | Responsibility | Default Tools |
|------|-------|-----------------|---|
| **Orchestrator** | RUNTIME | Orchestrate workflow, delegate tasks | All tools enabled |
| **TeamLeader** | PROJECT | Lead team, coordinate workers | Most tools (no core system access) |
| **Worker** | SESSION | Execute tasks, report status | Task-specific tools |
| **Planner** | RUNTIME | Analyze, plan, read-only | Read, analysis tools only |
| **Triage** | RUNTIME | Route, prioritize | Route, dispatch tools |
| **TeamMember** | SESSION | Individual task contributor | Individual task tools |

### Scope Hierarchy

```
GLOBAL (system-wide)
  ├─ Filesystem: /var/cache/css/
  ├─ TTL: Never expires (manual management)
  └─ Inherits to: APP
      │
      ├─ APP (application-level)
      │   ├─ Filesystem: ~/.cybersec/app/
      │   ├─ TTL: 30 days
      │   └─ Inherits to: PROJECT
      │       │
      │       ├─ PROJECT (project-specific)
      │       │   ├─ Filesystem: ~/.cybersec/app/projects/{project_id}/
      │       │   ├─ TTL: 7 days
      │       │   └─ Inherits to: RUNTIME
      │       │       │
      │       │       ├─ RUNTIME (active orchestrator process)
      │       │       │   ├─ Filesystem: /tmp/cybersec/runtime_{pid}/
      │       │       │   ├─ TTL: 60 minutes (process lifetime)
      │       │       │   └─ Inherits to: SESSION
      │       │       │       │
      │       │       │       └─ SESSION (task execution context)
      │       │       │           ├─ Filesystem: /tmp/cybersec/runtime_{pid}/sessions/{session_id}/
      │       │       │           ├─ TTL: 120 minutes (after completion: auto-cleanup)
      │       │       │           └─ No children
```

---

## Core Components

### 1. Permission Checking

**Decorators**:
```python
@require_permission("write", ScopeLevel.PROJECT)
async def create_project(name: str, scope_context: ScopeContext) -> Project:
    """Only roles with write access to PROJECT can create projects"""

@require_tool_permission("agents.execute")
async def execute_agent(agent_id: str, scope_context: ScopeContext) -> Result:
    """Only roles granted 'agents.execute' tool can execute agents"""
```

**Middleware**:
```python
class PermissionCheckingMiddleware:
    """ASGI middleware for all HTTP requests"""
    async def __call__(self, request: Request, call_next) -> Response:
        # 1. Extract token from request
        # 2. Validate scope_context from token
        # 3. Check path permissions (for route)
        # 4. Check tool permissions (for endpoint)
        # 5. Reject or allow request
```

**Direct Checking**:
```python
if not scope_context.has_permission(
    permission="execute",
    level=ScopeLevel.RUNTIME,
    role=Role.WORKER
):
    raise PermissionDenied(
        f"Worker cannot execute at RUNTIME level"
    )
```

### 2. Scope Management

**ScopeContext** (passed through all operations):
```python
class ScopeContext:
    """Encapsulates permission context for current operation"""
    role: Role  # Current role (Orchestrator, TeamLeader, etc.)
    scope_level: ScopeLevel  # Current scope (GLOBAL, APP, PROJECT, RUNTIME, SESSION)
    scope_id: str  # Identifier (project_id, session_id, etc.)
    timestamp: datetime  # When context created
    token: str  # JWT token for validation
    
    # Methods
    def has_permission(perm: str, level: ScopeLevel, role: Role) -> bool
    def get_filesystem_path() -> Path
    def get_parent_scope() -> ScopeContext
    def create_child_scope(...) -> ScopeContext
```

**scope_config.json** (per scope level):
```json
{
  "scope": "PROJECT",
  "scope_id": "proj_12345",
  "role_permissions": {
    "orchestrator": {
      "path": ["read", "write", "execute"],
      "tools": ["all"]
    },
    "team_leader": {
      "path": ["read", "write"],
      "tools": ["agents", "tasks", "skills"]
    }
  },
  "parent_scope": {
    "scope": "APP",
    "scope_id": "app_default"
  },
  "ttl_minutes": 420,
  "auto_cleanup": true
}
```

### 3. Process Models

**Development Mode** (3 separate processes):
```
Main Process (Planner)
├─ Permission: read-only, analysis tools
├─ Scope: RUNTIME
└─ Purpose: Deep inspection, planning

Main Process (Orchestrator)
├─ Permission: full control
├─ Scope: RUNTIME
└─ Purpose: Workflow orchestration

Main Process (Triage)
├─ Permission: routing, dispatch
├─ Scope: RUNTIME
└─ Purpose: Request routing & prioritization
```

**Assessment Modes** (Red/Blue/Purple) (2 processes + teams):
```
Main Process (Orchestrator)
├─ Permission: full control
├─ Scope: RUNTIME
└─ Child Processes: N Team Subprocesses
    │
    ├─ Team Subprocess 1
    │   ├─ Thread: TeamLeader
    │   │   ├─ Permission: team-level coordination
    │   │   ├─ Scope: PROJECT
    │   │   └─ Spawns: N Worker threads
    │   └─ Thread Pool: M Workers
    │       ├─ Permission: task execution
    │       ├─ Scope: SESSION
    │       └─ Purpose: Parallel task execution
    │
    └─ Team Subprocess N
        └─ (Same pattern as Team 1)

Main Process (Triage)
├─ Permission: routing & prioritization
├─ Scope: RUNTIME
└─ Purpose: Request queueing & dispatch
```

### 4. Module Integration Points

**Event System Integration**:
- EventBus respects scope_context when dispatching events
- Events scoped to SESSION cannot bubble up to PROJECT scope
- Permission check on subscriber registration (can topic subscriber call?)

**Working Memory Integration**:
- Memory store scoped to SESSION/RUNTIME
- Read permissions enforced on memory.get()
- Write permissions enforced on memory.set()

**Agent/Task Execution**:
- Agent/Task execution scoped to SESSION
- Inherits permissions from PROJECT scope
- Can request elevation (Orchestrator approval needed)

**Marketplace Integration**:
- Marketplace packages downloaded at PROJECT scope
- Tools/skills installed at PROJECT/RUNTIME scope
- Installation requires project write + tool permission

---

## Checklist: Permissions Module Implementation

- [ ] **Core Classes**
  - [ ] Role enum (ORCHESTRATOR, TEAM_LEADER, WORKER, PLANNER, TRIAGE, TEAM_MEMBER)
  - [ ] ScopeLevel enum (GLOBAL, APP, PROJECT, RUNTIME, SESSION)
  - [ ] Permission enum (READ, WRITE, EXECUTE)
  - [ ] ScopeContext class (role, scope_level, scope_id, token, methods)
  - [ ] PermissionPolicy class (stores path + tool permissions)

- [ ] **Decorators**
  - [ ] @require_permission(path_perm, level)
  - [ ] @require_tool_permission(tool_id)
  - [ ] @require_role(role_list)
  - [ ] @require_scope_level(level)

- [ ] **Middleware**
  - [ ] PermissionCheckingMiddleware (ASGI)
  - [ ] Token validation on request
  - [ ] Scope context extraction
  - [ ] Error handling (PermissionDenied, TokenInvalid)

- [ ] **Utilities**
  - [ ] get_filesystem_path(scope_context) → Path
  - [ ] validate_token(token_str) → ScopeContext
  - [ ] issue_token(scope_context, expires_in) → str
  - [ ] inherit_permissions(parent_context, child_level) → PermissionPolicy
  - [ ] load_scope_config(scope_level, scope_id) → Dict

- [ ] **Database Models**
  - [ ] PermissionGrant model (role, scope, permission_set)
  - [ ] ScopeSession model (scope_id, created_at, expires_at, auto_cleanup_at)
  - [ ] RolePermissionCache model (caches computed permissions)

- [ ] **Tests**
  - [ ] test_permission_inheritance (parent → child restrictions)
  - [ ] test_scope_context_creation (multi-level scopes)
  - [ ] test_decorator_enforcement (decorator blocks unauthorized calls)
  - [ ] test_middleware_rejection (unauthorized requests rejected)
  - [ ] test_role_based_access (6 roles, correct tool sets)
  - [ ] test_process_model_isolation (dev mode vs assessment modes)
  - [ ] test_token_expiry (session TTL, auto-cleanup)

- [ ] **Documentation**
  - [ ] Dual permission model explanation
  - [ ] Scope hierarchy diagram
  - [ ] Role definitions & tool access matrix
  - [ ] Code examples (decorators, middleware, direct checks)
  - [ ] Process model diagrams (dev vs assessment)
  - [ ] Integration guide (for modules consuming permissions)

---

## Module Pattern

```python
# src/css/modules/permissions/__init__.py
from .models import (
    Role, ScopeLevel, Permission,
    ScopeContext, PermissionPolicy
)
from .decorators import (
    require_permission, require_tool_permission,
    require_role, require_scope_level
)
from .middleware import PermissionCheckingMiddleware
from .utils import (
    get_filesystem_path, validate_token, issue_token,
    inherit_permissions, load_scope_config
)

__all__ = [
    'Role', 'ScopeLevel', 'Permission',
    'ScopeContext', 'PermissionPolicy',
    'require_permission', 'require_tool_permission',
    'require_role', 'require_scope_level',
    'PermissionCheckingMiddleware',
    'get_filesystem_path', 'validate_token', 'issue_token',
    'inherit_permissions', 'load_scope_config',
]
```

---

## Integration Guide

### For Other Modules

**Getting Current Scope Context**:
```python
# From middleware (already in request.state)
scope_context = request.state.scope_context

# Or from function parameter
async def my_handler(scope_context: ScopeContext):
    print(f"Current role: {scope_context.role}")
    print(f"Current scope: {scope_context.scope_level}")
```

**Checking Permissions**:
```python
from permissions import require_permission

@require_permission("write", ScopeLevel.PROJECT)
async def create_resource(data: Dict, scope_context: ScopeContext):
    # Only reachable if scope_context has write access
    return {"status": "created"}
```

**Enforcing Tool Permissions**:
```python
from permissions import require_tool_permission

@require_tool_permission("agents.orchestrate")
async def execute_orchestration(agent_id: str, scope_context: ScopeContext):
    # Only reachable if role is granted agents.orchestrate
    pass
```

**Creating Child Scope**:
```python
# When spawning subprocess/team/session
child_context = scope_context.create_child_scope(
    scope_level=ScopeLevel.SESSION,
    scope_id=f"session_{uuid4()}"
)
# child_context inherits parent permissions (may be restricted)
```

---

## Related Files

- **Role Definitions**: `src/css/modules/roles/` — Role types & capabilities
- **Scope Configuration**: `src/css/core/config/scope_config.json` — Scope settings
- **Tokens**: `src/css/core/auth/tokens.py` — JWT token generation/validation
- **Middleware**: `src/css/core/middleware/` — ASGI middleware stack
- **Database**: `src/css/core/db/entities/` — Permission grant models

---

## Key Decisions

1. **Dual Model**: Path permissions (hierarchical, restrictive) + Tool permissions (static, per-role)
2. **Scope Inheritance**: Child inherits parent FULLY unless explicitly restricted (not default-deny)
3. **Role Granularity**: 6 roles instead of 3 (adds Planner, Triage, TeamMember for workflow clarity)
4. **Process Isolation**: Development mode (3 processes) vs Assessment modes (2 + N teams)
5. **Auto-Cleanup**: SESSION scopes auto-delete after 120 min + completion
6. **No Privilege Escalation**: Roles cannot upgrade themselves; Orchestrator approval needed

---

## Success Criteria

✅ All 6 roles with distinct tool permission sets
✅ 5-level scope hierarchy with correct TTL per level
✅ Permission inheritance working (parent → child, restriction only)
✅ Decorators block unauthorized calls
✅ Middleware rejects unauthorized requests
✅ Process models (dev vs assessment) correctly isolated
✅ Token generation & validation working
✅ Database models for permission grants & scope sessions
✅ Full integration with EventBus, WorkingMemory, Agents, Tasks, Marketplace
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: See .plan/modules/module-audit-matrix.md for full audit results.
