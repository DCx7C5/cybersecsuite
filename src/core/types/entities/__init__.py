"""Entity types — domain entities, headers, and protocols."""

from .account import Account
from .agent import Agent
from .base import BaseAgent, BaseEntity, BaseRole, BaseSkill, BaseTool
from .headers.tool import ToolHeader
from .role import Role, get as get_role
from .skill import Skill
from .tool import Tool

__all__ = [
    # Base entities
    "BaseEntity",
    "BaseAgent",
    "BaseSkill",
    "BaseTool",
    "BaseRole",
    # Concrete entities
    "Tool",
    "Skill",
    "Role",
    "Agent",
    "Account",
    "ToolHeader",
    # Factory functions
    "get_role",
]
