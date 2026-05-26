# @sessions - Session Lifecycle and Audit Plan

**Status**: Planned runtime ownership; only `src/css/modules/sessions/__init__.py` and this contract currently exist.

## Purpose

Sessions own execution lifecycle state independent of projects:

- create, resume and end an agent session
- associate a session with an optional project
- maintain mode and status transitions
- provide the session identity consumed by memory, agents, approvals and git tracking

## Filesystem Ownership Question

Older planning content routed session filesystem management through `core/workspace` / `WorkingDirManager`. That ownership is not confirmed by the current source tree and must be re-evaluated before implementation. The durable contract is only:

- a session has isolated output/scratch state
- a project source directory is not implicitly the session output directory
- filesystem permissions must be enforced through the eventual permission boundary

## Git / Worktree Requirements

Phase 24 requirements retained here:

- session-owned git history for generated/modified artifacts where enabled
- one branch/worktree per parallel agent when concurrent file mutation is allowed
- merge strategy selected at session completion (`SQUASH`, `REBASE`, `OURS`, or manual)
- domain events and session-turn history remain complementary audit layers; git does not replace either

### Phase 24 Execution Order

| Stage | Required result |
|-------|-----------------|
| Tracking | initialize the session repository, implement `GitTracker`, and trigger commits after completed agent turns |
| Isolation | create/delete/list one agent branch and worktree for each concurrently mutating agent |
| Lifecycle | wire worktree creation/removal into the session agent lifecycle |
| Completion | merge session work with `SQUASH`, `REBASE`, `OURS`, or manual resolution |
| Reconciliation | remove or rename legacy `scope.py` worktree fields only after the canonical session-output owner is confirmed |

Branch naming contract:

```text
agent/{session_id[:8]}/{agent_id}
```

Do not implement the historical `core/workspace` destination until source and
architecture reconciliation confirms an actual owner for session output.

## Integration Points

| Component | Relationship |
|-----------|--------------|
| `modules/projects` | optional association to a registered project |
| `modules/agents` | session context injection and agent membership |
| `core/memory` | resume/end lifecycle persistence |
| `core/permissions` | path/tool grants for session operations |
| `modules/approvals` | approval state tied to a session |
| `core/events` | lifecycle/audit events |

## Implementation Gate

Before writing session lifecycle or filesystem code, inspect current source ownership and retire or normalize stale `working_dir`/`workspace` terminology consistently.

## Executable Owner Contract

### Exact File And Symbol Map

| Path | Reality / planned symbols |
|------|----------------------------|
| `src/css/modules/sessions/__init__.py` | Existing package stub; future stable exports only after runtime exists. |
| `src/css/modules/sessions/enums.py` | Planned `SessionStatus`, `SessionMode`. |
| `src/css/modules/sessions/models.py` | Planned `SessionRecord`, `to_context()`, `from_context()`. |
| `src/css/modules/sessions/manager.py` | Planned `SessionManager.create()`, `resume()`, `end()` and transition enforcement. |
| `src/css/modules/sessions/endpoints.py` | Planned CRUD/lifecycle router handlers. |
| `src/css/core/session.py` | Planned shared `SessionContext` primitive with `session_dir`; not a filesystem owner. |
| `src/css/core/streaming/sessions.py` | Existing/provisional session surface to reconcile or delegate after canonical module implementation. |

There is no confirmed `src/css/core/workspace/` or `working_dir` runtime
owner. Any todo text naming those paths is blocked by ownership reconciliation
and must be corrected before code is written.

### Live Todo Map

| Todo ID | Status | Execution boundary |
|---------|--------|--------------------|
| `sessions-lifecycle` | pending | Create enums and stateful manager behavior; reconcile provisional streaming session ownership. |
| `sessions-persistence` | pending | Persist the canonical context and lifecycle fields through `SessionRecord`. |
| `sessions-endpoints` | pending | Add thin HTTP handlers delegating to `SessionManager`. |
| `sessions-mode-layout`, `sessions-module-create` | pending | Do not implement filesystem layouts until session-output ownership is decided and stale path targets are repaired. |
| `git-session-init`, `git-tracker`, `git-worktree-manager`, `git-worktree-sessionmgr`, `git-merge-manager` | pending | Implement only beside the confirmed session artifact owner. |
| `git-scope-migration`, `git-tracking-docs`, `git-rules-update` | pending | Reconcile legacy references and policy without reviving unconfirmed packages. |

### Numbered Work Order And Validation

1. Define the `SessionContext`/status/mode/lifecycle/persistence API without
   allocating output directories.
2. Resolve the canonical isolated output owner and update affected tracker
   descriptions before implementing layout, Git repository, or worktree code.
3. Add endpoints over persisted lifecycle state; add Git isolation only when
   session artifact ownership is settled.
4. Validate package imports, allowed/invalid transitions, ORM context
   round-trips, route mounting, and temporary-repository Git/worktree behavior;
   run a dependency scan confirming no accidental `core/workspace` dependency.
