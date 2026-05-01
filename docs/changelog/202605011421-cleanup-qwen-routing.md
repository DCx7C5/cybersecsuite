# 2026-05-01 14:21: Cleanup + Qwen Switchable Logic + Legacy Fixes

## Status
✅ COMPLETE

## Changes

### 1. Root Documentation Cleanup
- Moved QWEN_*.md (5 files) → session folder
- Moved RUBBER_DUCK_*.md (3 files) → session folder
- Reason: Analysis docs are planning artifacts, not production code
- Kept: IMPLEMENTATION_GRAPH.md (locked architecture)

### 2. Response Injection Strategy Router
- New: `src/core/orchestration/response_strategy_router.py`
- Implements ResponseStrategyRouter (automatic strategy selection)
- QueryComplexity enum: simple/moderate/complex
- Switchable logic: decide_strategy() based on complexity
- Placeholder for Phase 2: Qwen triage integration

### 3. Legacy Qwen References Fixed
- File: `src/legacy/ai_proxy/providers/_providers.py`
- Changed: qwen0.8b → qwen3:0.6b (actual version)
- Changed: "Qwen 0.8B" → "Qwen3 0.6B" (display names)
- Reason: Align with released Qwen3 models

## Files Modified
- Root: 8 files moved to session
- New: `src/core/orchestration/response_strategy_router.py`
- Updated: `src/legacy/ai_proxy/providers/_providers.py`
- New: `src/core/orchestration/__init__.py`

## Next
- Ready for Phase 1a ModelExecutor extraction
- Strategy router available for integration
