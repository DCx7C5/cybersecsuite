"""Pydantic models for google_a2a internal message handling."""

from pydantic import BaseModel, Field
from typing import Optional, Callable


class InternalMessage(BaseModel):
    """Internal message format for google_a2a module.

    Used for routing messages between agents via Redis pub/sub.
    """

    role: str = Field(..., description="Message role (agent, assistant, user)")
    content: str = Field(default="", description="Message content")
    name: Optional[str] = Field(default=None, description="Agent name for agent role")
    parts: list[dict] = Field(default_factory=list, description="Message parts for complex content")


class MessageDispatcher:
    """Dispatcher for routing InternalMessage between agents.

    Handles publishing/subscribing to Redis channels.
    """

    def __init__(self, redis_client=None):
        """Initialize dispatcher.

        Args:
            redis_client: Optional Redis client for pub/sub
        """
        self.redis = redis_client
        self._subscribers: dict[str, list[Callable]] = {}

    async def dispatch(self, message: InternalMessage, channel: str = "default") -> None:
        """Dispatch a message to all subscribers of a channel.

        Args:
            message: The InternalMessage to dispatch
            channel: The channel to dispatch on
        """
        if channel in self._subscribers:
            for callback in self._subscribers[channel]:
                await callback(message)

    def subscribe(self, channel: str, callback: Callable) -> None:
        """Subscribe to a channel.

        Args:
            channel: The channel to subscribe to
            callback: Function to call when message received
        """
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)

    async def publish(self, message: InternalMessage, channel: str = "default") -> None:
        """Publish a message to Redis channel.

        Args:
            message: The InternalMessage to publish
            channel: The Redis channel
        """
        if self.redis:
            await self.redis.publish(
                channel, message.json(by_alias=True)
            )
        await self.dispatch(message, channel)
