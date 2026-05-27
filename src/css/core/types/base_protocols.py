"""Base protocol interfaces — foundational contracts for domain entities."""

from collections.abc import AsyncIterator
from typing import Any, Literal, Protocol, runtime_checkable


@runtime_checkable
class BaseCommunicator(Protocol):
    """Interface for asynchronous inter-entity messaging.

    Communicators wrap a message dispatcher to provide a high-level async interface
    for sending messages between agents, skills, and other domain entities.

    Properties:
        entity_id: Unique identifier of the sending entity (e.g., "agents:analyst")
        dispatcher: Underlying message dispatch infrastructure

    Any implementation must support:
        - async send(to_id, payload, msg_type, routing_mode)
        - async post_message(content, target, msg_type, routing_mode)
        - async subscribe(handler, message_types)
        - async unsubscribe(handler)
    """

    @property
    def entity_id(self) -> str:
        """Canonical identifier of the sending entity."""
        ...

    @property
    def dispatcher(self) -> Any:  # MessageDispatcher
        """Underlying message dispatcher infrastructure."""
        ...

    async def send(
        self,
        to_id: str,
        payload: Any,
        *,
        msg_type: str = "task",
        routing_mode: Literal["direct", "shortest_path"] = "shortest_path",
    ) -> None:
        """Send a structured message to a specific recipient entity."""
        ...

    async def post_message(
        self,
        content: str,
        target: str = "all",
        *,
        msg_type: str = "task",
        routing_mode: Literal["direct", "shortest_path"] = "shortest_path",
    ) -> None:
        """Post a plain-text message (broadcast or direct)."""
        ...

    async def subscribe(
        self, handler: Any, message_types: list[str] | None = None
    ) -> None:
        """Subscribe to incoming messages (optionally filtered by type)."""
        ...

    async def unsubscribe(self, handler: Any) -> None:
        """Unsubscribe a handler from incoming messages."""
        ...


@runtime_checkable
class BaseAgentLike(Protocol):
    """Protocol for agent-like entities (replaces AgentLike)."""

    @property
    def header(self) -> object: ...

    @property
    def communicator(self) -> object | None: ...

    def to_dict(self) -> dict[str, Any]: ...

    @property
    def skill_ids(self) -> list[str]: ...

    @property
    def tools(self) -> list[object]: ...

    @property
    def is_orchestrator(self) -> bool: ...

    @property
    def is_default(self) -> bool: ...


@runtime_checkable
class BaseSkillLike(Protocol):
    """Protocol for skill-like entities (replaces SkillLike)."""

    @property
    def header(self) -> object: ...

    @property
    def communicator(self) -> object | None: ...

    def to_dict(self) -> dict[str, Any]: ...

    @property
    def kind(self) -> str: ...

    @property
    def provider(self) -> str: ...

    @property
    def source_path(self) -> str | None: ...

    @property
    def tools(self) -> list[object]: ...


@runtime_checkable
class BaseToolLike(Protocol):
    """Protocol for tool-like entities (replaces ToolLike)."""

    @property
    def header(self) -> object: ...

    @property
    def communicator(self) -> object | None: ...

    def to_dict(self) -> dict[str, Any]: ...

    @property
    def tool_name(self) -> str: ...

    @property
    def display_name(self) -> str: ...

    @property
    def tool_type(self) -> str: ...

    @property
    def input_schema(self) -> dict[str, Any]: ...

    @property
    def is_mcp(self) -> bool: ...

    def is_available(self) -> bool: ...


@runtime_checkable
class BaseTeamMemberLike(Protocol):
    """Protocol for team member entities (replaces TeamMemberLike)."""

    @property
    def header(self) -> object: ...

    @property
    def communicator(self) -> object | None: ...

    def to_dict(self) -> dict[str, Any]: ...

    @property
    def agent_id(self) -> str: ...

    @property
    def team_id(self) -> str: ...

    @property
    def is_active(self) -> bool: ...


@runtime_checkable
class BaseLLMAdapter(Protocol):
    """Protocol for LLM provider adapters (replaces ABC BaseApiServiceClient).

    All provider adapters (native SDK, HTTP, custom, complex authentication) must implement
    this protocol. The streaming contract is: always return AsyncIterator[StreamChunk],
    even for buffered calls (yield one final chunk).
    """

    provider_id: str
    api_key: str | None
    base_url: str | None

    async def get_models(self) -> list[Any]:
        """Get available models with per-model feature flags."""
        ...

    async def call_llm(
        self,
        model_id: str,
        messages: list[Any],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        streaming: bool = True,
        **kwargs: Any,
    ) -> AsyncIterator[Any]:
        """Call LLM with streaming support — yields StreamChunks."""
        ...

    async def call_llm_buffered(
        self,
        model_id: str,
        messages: list[Any],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Buffered call — accumulate chunks and return LLMResponse."""
        ...

    def supports_feature(self, model: Any, feature: str) -> bool:
        """Check if model supports a feature."""
        ...

    @property
    def cache_capability(self) -> Any:
        """Return CachingCapability enum value for this adapter.

        Used by PromptCacheManager to determine multi-tier caching strategy.
        Implementations should return CachingCapability.<appropriate_value>.
        """
        ...


__all__ = [
    "BaseCommunicator",
    "BaseAgentLike",
    "BaseSkillLike",
    "BaseToolLike",
    "BaseTeamMemberLike",
    "BaseLLMAdapter",
]
