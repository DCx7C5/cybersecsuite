"""Base protocol for executable skills."""


from typing import Any, Protocol, runtime_checkable

from css.core.sdks.context import ConversationContext

from .models import SkillParameter, SkillResult


@runtime_checkable
class BaseSkill(Protocol):
    """Executable skill contract used by the runtime registry."""

    name: str
    description: str
    parameters: list[SkillParameter]

    async def execute(
        self,
        params: dict[str, Any],
        context: ConversationContext,
    ) -> SkillResult:
        """Execute skill logic with structured params and conversation context."""
        ...

