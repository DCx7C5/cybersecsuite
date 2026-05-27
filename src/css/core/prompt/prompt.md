# core/prompt — Verified Prompt Boundary

**Location**: `src/css/core/prompt/`
**Status**: Scaffold-only package; no runtime symbols yet.
**Tracker authority**: `.plan/session.db`

## Purpose

`core/prompt` is the planned cross-cutting boundary for **verified prompt
ingestion**, not the prompt registry store.

- `modules/prompts` owns prompt definitions, rendering, CRUD, and marketplace
  prompt catalog linking.
- `core/securemd` owns signature integrity and trusted-body release.
- `core/serializers` owns strict Markdown/frontmatter parsing.
- `core/prompt` will own the orchestration contract that ensures only verified
  marketplace-origin Markdown reaches execution consumers.

## Current Source Reality

| File | Status |
|------|--------|
| `__init__.py` | Empty scaffold |
| `prompt.md` | Owner specification (this file) |

Observed from source scan (`scripts/codebase_dependency_analyzer.py`, 2026-05-27):

- No imports currently target `css.core.prompt`.
- No code in `core/prompt` imports other runtime surfaces yet.
- Prompt security flow remains distributed across:
  `core/serializers`, `core/securemd`, and planned module-side prompt wiring.

## Dependency Snapshot (2026-05-27)

Global edge totals from `src/css` scan:

- `core -> core`: 204 imports
- `core -> modules`: 12 imports
- `core -> api_services`: 1 import

Current `core -> modules` edges:

1. `core/events -> modules/hooks` (3)
2. `core/tools -> modules/tools` (2)
3. `core/asgi -> modules/tools` (1)
4. `core/db -> modules/teams` (1)
5. `core/sdks -> modules/llm_proxy` (1)
6. `core/streaming -> modules/{agents,chat,projects,teams}` (4)

Current `core -> api_services` edge:

1. `core/sdks/adapters/deepseek.py -> api_services/deepseek/service.py` (1)

## Planned Contract

Before `securemd44-context-ingestion-gate` can be completed, introduce a
single runtime path in `core/prompt` that:

1. Accepts marketplace-origin Markdown payload metadata.
2. Parses strict frontmatter through `core/serializers`.
3. Verifies signer + content integrity through `core/securemd`.
4. Returns a verified prompt body (or typed rejection) for
   `modules/prompts`/agent execution consumers.

This package must not duplicate prompt registry CRUD or marketplace preview
display behavior.

## Validation

- Dependency analyzer on `src/css/core/prompt/`, `src/css/core/securemd/`,
  and `src/css/modules/prompts/`.
- Focused Ruff + basedpyright for touched files.
- Prompt security integration tests (signed/unsigned/tampered/wrong-key paths)
  once runtime symbols are implemented.
