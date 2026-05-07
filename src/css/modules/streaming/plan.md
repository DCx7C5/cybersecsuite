# modules/streaming — Streaming Runner

## Purpose
High-level agent streaming runner (`QueryExecutor`). Lives in modules (not core) because
it depends on `modules/agents` (AgentExecutor) and `modules/teams` (TeamLeader).

Core streaming infra (ClientPool, SessionManager, hooks) lives in `core/streaming/`.

## Status: 🟡 In progress

## Files
- `runner.py` — QueryExecutor: provider-agnostic multi-turn agent runner

## Planned
- `streaming.py` — stream_query implementation (referenced by runner, not yet built)

## Import Rule
- Imports FROM: `core/streaming/` (ClientPool), `modules/agents/`, `modules/teams/`
- Must NOT import from: other modules (except agents + teams which are direct deps)
