"""Compatibility re-export for shared pipeline primitives.

Canonical implementation lives in ``css.core.pipeline``.
"""

from css.core.pipeline import (
    BufferStage,
    ExecuteStage,
    FilterStage,
    MapStage,
    ObserveStage,
    PassthroughStage,
    Stage,
    pipe,
)

__all__ = [
    "pipe",
    "Stage",
    "PassthroughStage",
    "BufferStage",
    "FilterStage",
    "MapStage",
    "ExecuteStage",
    "ObserveStage",
]
