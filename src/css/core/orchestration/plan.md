# core/orchestration — Client Pool & Response Strategy Router

**Location**: `src/css/core/orchestration/`
**Status**: ✅ Phase 1 Complete | 🟡 Phase 6 P5 pipeline integration pending

---

## Purpose

Shared orchestration infrastructure: LLM client pool management and response strategy routing. Lives in `core/` because it is consumed by both `modules/agents/` and `modules/workflows/`.

---

## Files

| File | Purpose | Status |
|------|---------|--------|
| `client_pool.py` | `ClientPool` — pool of LLM client instances for concurrent sessions | ✅ Done |
| `response_strategy_router.py` | `ResponseStrategyRouter` — routes responses to correct handler | ✅ Done |

---

## Integration Points

| Consumer | What it uses |
|----------|-------------|
| `modules/agents/` | `ClientPool.acquire(session_id)` for per-session clients |
| `modules/workflows/` | `ResponseStrategyRouter` for multi-step execution |
| Phase 6 P5 | Pipeline `observe()` stage will wrap `ClientPool` calls |

---

## Todos

All Phase 1 orchestration todos (`orchestrator-1-schema` through `orchestrator-9-result-merging`) are ✅ Done.

Pending:
- Phase 6 P5: Wire `ClientPool` into async generator pipeline (`p6-pipeline-*` todos)
