# @approvals - Human Approval Workflow Plan
Approval workflows remain module-owned and integrate with `core/permissions`; they are not folded into the core package by assumption.

**Status**: Planned Phase 26 module; runtime package not yet implemented.


## Purpose

High-risk agent actions must pause for an explicit human decision when policy requires it.

## Execution Contract

```text
tool request -> permission/policy evaluation
  -> allowed: execute
  -> denied: fail without execution
  -> approval required:
       persist pending request
       emit `approval.requested`
       push to subscribed frontend session
       await approve/reject/timeout decision
       execute only after approval
```

## Required Domain Types

- `ApprovalRequest`: id, session id, agent id, action type/payload, status, timestamps, decision actor/reason and timeout
- `ApprovalPolicy`: action patterns, permitted scope, exempt roles, timeout action and timeout seconds
- `ApprovalStatus`: `PENDING`, `APPROVED`, `REJECTED`, `EXPIRED`
- `ApprovalDecision`: `REQUIRED`, `ALLOWED`, `DENIED`

Value types use `msgspec.Struct`; ORM entities use `BaseModel` and semantic field helpers where applicable.

## Required Runtime Surfaces

| Surface | Requirement |
|---------|-------------|
| Persistence | request and policy ORM models; indexed pending-expiration lookups |
| Gate | resolve policies before execution and return a typed decision |
| Channel | async wait/resolution by request id with timeout behavior |
| API | list pending/history, get request, approve and reject |
| Push | websocket event for requested/resolved approvals |
| Audit | OpenObserve/event emission for approve/reject/expire lifecycle |

## Integration Points

- `core/permissions`: permission result can require approval.
- `core/tools` / `modules/agents`: execution must pause before the tool runs.
- `modules/sessions`: approval visibility and lifecycle are session-scoped.
- `core/events`: `approval.requested`, `approved`, `rejected`, `expired`.
- `modules/graphs`: approval nodes may appear in operational workflow graphs.

## Seed Policy Baseline

Initial policies should require human review for destructive file writes and high-risk network/response actions; read-only operations may be allowed unless a stricter profile applies.
