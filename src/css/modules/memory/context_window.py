"""Context window management — rolling token budget with message eviction.

Implements sliding window of messages within a fixed token budget,
with automatic eviction of oldest messages when context overflows.
"""

from __future__ import annotations

import msgspec
from datetime import datetime
from typing import Any

from css.core.types.api_services import BaseMessage


class TokenEstimate(msgspec.Struct):
    """Token count estimate for a message or text.
    
    Attributes:
        message_tokens: Tokens consumed by message content
        total_tokens: Total tokens (including overhead)
        estimated: True if estimated (not exact), False if counted
    """
    message_tokens: int
    total_tokens: int
    estimated: bool = True


class ContextWindow(msgspec.Struct):
    """Sliding context window with rolling token budget.
    
    Maintains a FIFO queue of messages within max_tokens capacity.
    When adding a message would exceed capacity, oldest messages are evicted
    until the new message fits (or only new message remains if it exceeds budget).
    
    Attributes:
        max_tokens: Maximum tokens allowed in context window (default 8192)
        messages: Queue of messages in current context
        total_tokens: Current token count in context
        evicted_count: Number of messages evicted due to overflow
        created_at: When window was created
        updated_at: When window was last modified
    """

    max_tokens: int = 8192
    messages: list[BaseMessage] = msgspec.field(default_factory=list)
    total_tokens: int = 0
    evicted_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Initialize timestamps on creation."""
        now = datetime.utcnow()
        if self.created_at is None:
            object.__setattr__(self, 'created_at', now)
        if self.updated_at is None:
            object.__setattr__(self, 'updated_at', now)

    def estimate_tokens(self, content: str) -> TokenEstimate:
        """Estimate token count for text content.
        
        Uses rough heuristic: ~4 characters per token.
        Should be overridden with actual tokenizer in provider-specific implementations.
        
        Args:
            content: Text content to estimate
            
        Returns:
            TokenEstimate with message_tokens and total_tokens (with overhead)
        """
        # Rough estimation: 4 chars per token + 4 token overhead per message
        message_tokens = max(1, len(content) // 4)
        total_tokens = message_tokens + 4  # Add message framing overhead
        return TokenEstimate(
            message_tokens=message_tokens,
            total_tokens=total_tokens,
            estimated=True
        )

    def get_message_tokens(self, message: BaseMessage) -> int:
        """Get token count for a message (estimate).
        
        Args:
            message: Message to estimate
            
        Returns:
            Token count estimate
        """
        estimate = self.estimate_tokens(message.content)
        return estimate.total_tokens

    def can_fit(self, message: BaseMessage) -> bool:
        """Check if message fits in remaining capacity without eviction.
        
        Args:
            message: Message to check
            
        Returns:
            True if message fits without evicting other messages
        """
        tokens = self.get_message_tokens(message)
        return self.total_tokens + tokens <= self.max_tokens

    def add_message(self, message: BaseMessage, force: bool = False) -> bool:
        """Add message to context window, evicting old messages if needed.
        
        Implements rolling eviction: removes oldest messages until new message fits.
        If force=True, keeps message even if it alone exceeds max_tokens.
        
        Args:
            message: Message to add
            force: If True, add even if message alone exceeds max_tokens
            
        Returns:
            True if message was added, False if it couldn't fit and force=False
        """
        tokens = self.get_message_tokens(message)
        
        # If message alone exceeds max and force=False, reject it
        if tokens > self.max_tokens and not force:
            return False
        
        # Evict old messages until space is available
        new_total = self.total_tokens + tokens
        while new_total > self.max_tokens and self.messages:
            removed = self.messages.pop(0)
            removed_tokens = self.get_message_tokens(removed)
            new_total -= removed_tokens
            object.__setattr__(self, 'evicted_count', self.evicted_count + 1)
        
        # Add new message
        self.messages.append(message)
        object.__setattr__(self, 'total_tokens', new_total)
        object.__setattr__(self, 'updated_at', datetime.utcnow())
        return True

    def get_messages(self) -> list[BaseMessage]:
        """Get all messages currently in context window.
        
        Returns:
            List of messages in FIFO order
        """
        return self.messages.copy()

    def get_available_tokens(self) -> int:
        """Get remaining token capacity in window.
        
        Returns:
            Number of tokens available before overflow
        """
        return max(0, self.max_tokens - self.total_tokens)

    def get_utilization_pct(self) -> float:
        """Get context window utilization as percentage.
        
        Returns:
            Percentage of max_tokens currently used (0-100+, >100 means overflow)
        """
        if self.max_tokens == 0:
            return 0.0
        return (self.total_tokens / self.max_tokens) * 100.0

    def to_provider_format(self) -> list[dict[str, Any]]:
        """Convert messages to provider API format.
        
        Transforms BaseMessage objects to OpenAI-compatible format:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        
        This format is compatible with OpenAI, Anthropic, and most LLM APIs.
        Provider-specific implementations can override for custom formats.
        
        Returns:
            List of message dicts with 'role' and 'content' keys
        """
        result = []
        for msg in self.messages:
            result.append({
                "role": msg.role.value if hasattr(msg.role, 'value') else str(msg.role),
                "content": msg.content
            })
        return result

    def clear(self) -> None:
        """Clear all messages from context window.
        
        Resets tokens but preserves eviction count and timestamps.
        """
        object.__setattr__(self, 'messages', [])
        object.__setattr__(self, 'total_tokens', 0)
        object.__setattr__(self, 'updated_at', datetime.utcnow())

    def reset(self) -> None:
        """Reset context window to initial state.
        
        Clears messages, tokens, and eviction count.
        Keeps created_at timestamp.
        """
        self.clear()
        object.__setattr__(self, 'evicted_count', 0)


class WindowConfig(msgspec.Struct):
    """Configuration for context window behavior.
    
    Attributes:
        max_tokens: Maximum tokens per window
        reserve_tokens: Tokens to reserve for response generation
        eviction_strategy: How to evict messages ('oldest', 'smallest', 'summary')
        enable_summary_on_evict: Create summary when many messages evicted?
    """
    max_tokens: int = 8192
    reserve_tokens: int = 1024
    eviction_strategy: str = "oldest"
    enable_summary_on_evict: bool = False

    @property
    def effective_max(self) -> int:
        """Get effective max tokens for input (accounting for reserve).
        
        Returns:
            max_tokens - reserve_tokens
        """
        return max(0, self.max_tokens - self.reserve_tokens)
