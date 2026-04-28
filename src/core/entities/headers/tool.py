from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.entities.headers.base import BaseToolHeader


@dataclass
class ToolHeader(BaseToolHeader):
    """Concrete header for a live callable tool.

    Extends ``BaseToolHeader`` (name, description, version, tags, tier, category…)
    with the execution-facing metadata needed to surface a tool in an agent SDK
    or MCP server:

    ``parameters`` — JSON Schema object describing accepted inputs, identical
    to the ``input_schema`` / ``parameters`` field in the Anthropic API.

    ``return_type`` — informal description of what the tool returns
    (e.g. ``"object"``, ``"string"``, ``"array"``).

    ``examples`` — optional list of ``{input, output}`` pairs used for
    documentation and few-shot prompting.
    """

    parameters: dict[str, Any] = field(default_factory=dict)
    return_type: str = "object"
    examples: list[dict[str, Any]] = field(default_factory=list)
