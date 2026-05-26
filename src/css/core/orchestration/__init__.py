"""
Core orchestration module.

Pattern: Orchestration logic is split across multiple locations:
- css.core.asgi.process → ProcessManager (process lifecycle)
- css.modules.strategies → response_strategy_router (routing/strategy selection)
- css.modules.teams → orchestrator (team-level task orchestration)

This module serves as a documentation anchor and re-exports key components.

Architecture Note:
  Orchestration in CyberSecSuite follows a distributed pattern:
  1. ProcessManager (core/asgi/process.py) — manages Uvicorn/ASGI lifecycle
  2. ResponseStrategyRouter (modules/strategies/) — selects response strategy based on query complexity
  3. TeamOrchestrator (modules/teams/) — coordinates team/agent execution
  
  This separation allows each concern (process, routing, team coordination)
  to be independently tested and versioned within their respective domains.

Future (Phase 34+):
  - Dependency Map will document cross-module orchestration flows
  - Potential unified registry for all orchestrators may be added here
"""

try:
    # Import process-level orchestration
    from css.core.asgi.process import ProcessManager, UvicornProcessManager
except ImportError:
    # Handle missing dependencies gracefully
    ProcessManager = None
    UvicornProcessManager = None

__all__ = [
    "ProcessManager",
    "UvicornProcessManager",
]
