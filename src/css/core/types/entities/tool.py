from __future__ import annotations

from dataclasses import dataclass

from ..base import BaseTool
from ..headers import BaseToolHeader


@dataclass
class Tool(BaseTool):
    """Concrete callable tools with full execution metadata.

    Extends ``BaseTool`` (catalog identity, tool_type, MCP/SDK wiring) with:

    ``header`` — typed ``ToolHeader`` carrying the parameter schema, return
    type description, and usage examples surfaced to the agents SDK.

    ``skill_id`` — optional ID of the parent ``Skill`` that owns this tools.
    Populated by the loader when a tools is declared inside a SKILL.md.

    ``fn_path`` — dotted importable path to the backing callable
    (e.g. ``"cssmcp.cybersec.vault_tool.vault_scaffold"``). Used for
    dynamic dispatch without importing the full MCP server module.
    """

    header: BaseToolHeader | None = None
    skill_id: str | None = None
    fn_path: str | None = None

    @property
    def qualified_name(self) -> str:
        """``skill_id:tool_name`` when part of a skill, otherwise just ``tool_name``."""
        if self.skill_id:
            return f"{self.skill_id}:{self.tool_name}"
        return self.tool_name
