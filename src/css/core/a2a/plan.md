# core/a2a — A2A Protocol Layer

**Location**: `src/css/core/a2a/`
**Status**: ✅ Implemented (moved from google_a2a)

## Purpose

Shared A2A protocol types used by both `modules/css_a2a/` (internal fast protocol) and `modules/google_a2a/` (external Google A2A adapter). Lives in `core/` so both modules can import without circular dependencies.

## Files

| File | Contents |
|------|---------|
| `enums.py` | `TaskState`, `MessageRole`, `PartType`, `StreamState`, `ResponseInjectionStrategy` |
| `models.py` | `Message`, `Task`, `TaskStatus`, `TaskArtifact`, `TextPart`, `FilePart`, `DataPart`, `Part` |
| `types.py` | `AgentCard`, `A2AConfig`, `PauseRequest`, `ResponseInjection`, `StreamingState`, `StreamingController`, `ToolMetadata` |

## Integration Points

| Consumer | What it uses |
|----------|-------------|
| `modules/css_a2a/` | `TaskState`, `MessageRole`, `Message`, `Task`, `TaskStatus`, `TaskArtifact` |
| `modules/google_a2a/` | All — full protocol types |
