from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.entities.base import BaseTool, BaseSkill
from core.entities.headers.tool import ToolHeader


@dataclass
class Tool(BaseTool):
    """Concrete callable tool with full execution metadata.

    Extends ``BaseTool`` (catalog identity, tool_type, MCP/SDK wiring) with:

    ``header`` — typed ``ToolHeader`` carrying the parameter schema, return
    type description, and usage examples surfaced to the agent SDK.

    ``skill_id`` — optional ID of the parent ``Skill`` that owns this tool.
    Populated by the loader when a tool is declared inside a SKILL.md.

    ``skill`` — optional resolved ``BaseSkill`` reference. ``None`` until
    explicitly hydrated (e.g. by ``SkillRegistry.resolve_tools()``).

    ``fn_path`` — dotted importable path to the backing callable
    (e.g. ``"cssmcp.cybersec.vault_tool.vault_scaffold"``). Used for
    dynamic dispatch without importing the full MCP server module.
    """

    header: ToolHeader | None = None
    skill_id: str | None = None
    skill: BaseSkill | None = None
    fn_path: str | None = None

    @property
    def is_standalone(self) -> bool:
        """True when this tool has no parent skill."""
        return self.skill_id is None

    @property
    def qualified_name(self) -> str:
        """``skill_id:tool_name`` when part of a skill, otherwise just ``tool_name``."""
        if self.skill_id:
            return f"{self.skill_id}:{self.tool_name}"
        return self.tool_name

    def as_api_block(self) -> dict[str, Any]:
        """Return the Anthropic API tool block for this tool.

        Handles all three tool_type families:
        - ``mcp_*``     → ``{"type": "mcp", "server_name": ..., "tool_name": ...}``  (future)
        - ``sdk_beta``  → ``{"type": <sdk_type_string>, ...}``
        - ``sdk_builtin`` / others → ``{"name": ..., "description": ..., "input_schema": ...}``
        """
        if self.sdk_type_string:
            block: dict[str, Any] = {"type": self.sdk_type_string}
            if self.required_beta:
                block["beta"] = self.required_beta
            return block

        schema = self.input_schema
        if not schema and self.header and self.header.parameters:
            schema = {"type": "object", "properties": self.header.parameters}

        return {
            "name": self.mcp_tool_name,
            "description": self.header.description if self.header else "",
            "input_schema": schema or {"type": "object", "properties": {}},
        }
