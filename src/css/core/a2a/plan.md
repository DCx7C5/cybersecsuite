# core/a2a — A2A Protocol Core

## Purpose
Shared A2A (Agent-to-Agent) protocol primitives used by both `modules/css_a2a` and `modules/google_a2a`.
Core layer only — no implementation, only shared enums, protocols, and base types.

## Status: 🟡 Partially restored (enums only)

## Files
- `enums.py` — TaskState, MessageRole, PartType, StreamState, ResponseInjectionStrategy
- `__init__.py` — re-exports enums

## Planned (not yet built)
- `models.py` — shared A2A message models (TextPart, FilePart, Message, Task)
- `types.py` — A2AConfig, AgentCard, StreamingController

## Import Rule
Both `modules/css_a2a` and `modules/google_a2a` import from here.
Neither module should import from the other.
