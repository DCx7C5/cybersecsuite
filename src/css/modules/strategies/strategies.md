# Strategies Module

**Status**: 🟡 Partial Runtime | **Phase**: 19 (Module Restructuring + Sessions)

## Purpose
Strategy selection and execution for agent task routing.

## Current Reality

- `pipeline.py` provides the route stage used by chat execution.
- `response_strategy_router.py` maps triage output to `ResponseInjectionStrategy`.
- Complexity classification consumes the canonical
  `css.modules.triage.classify_query()` API.
- No root-level `core/routing.py` facade is retained; strategy routing remains
  module-owned unless Phase 13 introduces a distinct provider router.

## TODOs
- `strategies-impl` (Phase 19)

## Dependencies
- `src/css/core/base/`
- `src/css/modules/triage/`
- `src/css/modules/a2a_google/`

## Implementation Contract

- Keep response injection strategy routing in this module.
- Keep provider budget/circuit-breaker routing in
  `src/css/core/resilience/routing/`; it is a different policy layer.
- Consume only the public `css.modules.triage` classification API.

## Validation

- Verify simple/moderate/complex triage outcomes map deterministically to
  injection strategies.
- Verify chat pipeline routing imports this module and no root
  `css.core.routing` facade remains.
