"""Entity types — domain entities, headers, and protocols."""

from .account import Account
from .agent import Agent
from ..base import BaseAgent, BaseEntity, BaseRole, BaseSkill, BaseTool
from ..headers import BaseToolHeader
from .role import Role, get as get_role
from .skill import Skill
from .tool import Tool


__all__ = [
    # Base entities
    "BaseEntity",
    "BaseAgent",
    "BaseSkill",
    "BaseRole",
    "BaseTool",
    # Concrete entities
    "Tool",
    "Skill",
    "Role",
    "Agent",
    "Account",
    "BaseToolHeader",
    # Factory functions
    "get_role",
]
