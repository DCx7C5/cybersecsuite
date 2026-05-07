"""Abstract base header — minimal metadata for all domain entities."""
from abc import ABC
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BaseHeader(ABC):
    """Root metadata header for all domain entities."""
    
    name: str = ""
    description: str = ""


@dataclass
class BaseToolHeader(BaseHeader):
    """Concrete header for a live callable tools.

    Extends ``BaseToolHeader`` (name, description, version, tags, tier, category…)
    with the execution-facing metadata needed to surface a tools in an agents SDK
    or MCP server:

    ``parameters`` — JSON Schema object describing accepted inputs, identical
    to the ``input_schema`` / ``parameters`` field in the Anthropic API.

    ``return_type`` — informal description of what the tools returns
    (e.g. ``"object"``, ``"string"``, ``"array"``).

    ``examples`` — optional list of ``{input, output}`` pairs used for
    documentation and few-shot prompting.
    """

    parameters: dict[str, Any] = field(default_factory=dict)
    return_type: str = "object"
    examples: list[dict[str, Any]] = field(default_factory=list)



__all__ = ["BaseHeader", "BaseToolHeader"]
