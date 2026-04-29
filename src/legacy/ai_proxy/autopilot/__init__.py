"""
Autopilot module — autonomous Claude execution with checkpoints and cost tracking.

Provides:
- executor: Staged commit execution with rollback capability
- checkpoints: Human-in-the-loop pause points and budget enforcement
- cost_estimator: Pre-request token estimation and cost calculation
"""


__all__ = [
    "executor",
    "checkpoints",
    "cost_estimator",
]
