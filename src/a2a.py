"""Compatibility module — re-exports legacy.a2a at root level for dynamic imports.

This allows code to use both:
  - Direct: from a2a.models import AgentCard
  - Dynamic: from a2a import models (happens at runtime)
  - Legacy: from legacy.a2a.models import AgentCard

The sys.modules hack makes 'a2a' behave as an alias for 'legacy.a2a'.
"""

from legacy import a2a as _a2a
import sys

sys.modules['a2a'] = _a2a

__all__ = ['_a2a']
