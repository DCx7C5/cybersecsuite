"""Strategies module enums."""

from enum import Enum


class QueryComplexity(str, Enum):
    """Query complexity level for strategy selection."""

    SIMPLE = "simple"      # Binary yes/no, validation -> INJECT
    MODERATE = "moderate"  # Routing decision, classification -> PREPEND
    COMPLEX = "complex"    # Multi-step reasoning, synthesis -> CHAIN

