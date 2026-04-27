"""AIProviderContext — contextual AI provider selection with request/response context management.

Referenz:
    plan.md T0-INF-004a — AIProviderContext class
    plan.md T0-INF-004b — AIProviderContext ORM model
    src/llm/client.py — LLM client integration
    src/ai_proxy/routing/combo.py — Routing engine
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from tortoise import fields
from tortoise.models import Model
from tortoise.transactions import in_transaction

logger = logging.getLogger("llm.ai_provider_context")


class AIProviderType(str, Enum):
    """AI provider types supported by CyberSecSuite."""

    claude = "claude"
    openai = "openai"
    gemini = "gemini"
    copilot = "copilot"
    grok = "grok"
    cursor = "cursor"
    ollama_local = "ollama_local"


class ContextSource(str, Enum):
    """Source of context information."""

    user_session = "user_session"
    api_request = "api_request"
    agent_orchestration = "agent_orchestration"
    background_task = "background_task"
    system_config = "system_config"


@dataclass
class AIProviderContext:
    """
    Runtime context for AI provider selection and execution.

    Captures request/response lifecycle with metrics, preferences, and
    fallback strategy. Enables provider switching, rate limiting, and
    cost optimization.

    Attributes:
        provider: Selected AI provider type
        model: Specific model identifier (e.g., "gpt-4o", "claude-3-5-sonnet")
        request_id: Unique request identifier for tracking
        session_id: Optional session identifier for context grouping
        priority: Execution priority (1-10, 10 highest)
        max_tokens: Token limit for this request
        temperature: Sampling temperature (0.0-2.0)
        system_prompt: System prompt injection
        context_source: Source of context information
        metadata: Arbitrary additional context
        created_at: Timestamp when context was created
        expires_at: Optional expiration time for cached context
        budget_remaining: Remaining budget in cents for this request
        retry_count: Number of retries attempted
        fallback_providers: List of fallback providers in priority order
    """

    provider: AIProviderType
    model: str
    request_id: str
    session_id: str | None = None
    priority: int = 5
    max_tokens: int = 4096
    temperature: float = 0.7
    system_prompt: str = ""
    context_source: ContextSource = ContextSource.api_request
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    budget_remaining: int = 10000  # cents
    retry_count: int = 0
    fallback_providers: list[AIProviderType] = field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        """Check if context has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def age_seconds(self) -> float:
        """Get age of context in seconds."""
        return (datetime.utcnow() - self.created_at).total_seconds()

    def to_headers(self) -> dict[str, str]:
        """Convert context to HTTP headers for propagation."""
        return {
            "X-AI-Provider": self.provider.value,
            "X-AI-Model": self.model,
            "X-Request-ID": self.request_id,
            "X-Session-ID": self.session_id or "",
            "X-Priority": str(self.priority),
            "X-Max-Tokens": str(self.max_tokens),
            "X-Temperature": str(self.temperature),
        }

    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> AIProviderContext:
        """Create context from HTTP headers."""
        return cls(
            provider=AIProviderType(headers.get("X-AI-Provider", "claude")),
            model=headers.get("X-AI-Model", "claude-3-5-sonnet-20241022"),
            request_id=headers.get("X-Request-ID", "unknown"),
            session_id=headers.get("X-Session-ID") or None,
            priority=int(headers.get("X-Priority", "5")),
            max_tokens=int(headers.get("X-Max-Tokens", "4096")),
            temperature=float(headers.get("X-Temperature", "0.7")),
        )


class AIProviderContextSchema(BaseModel):
    """Pydantic schema for AIProviderContext serialization."""

    provider: AIProviderType
    model: str
    request_id: str
    session_id: str | None = None
    priority: int = Field(ge=1, le=10, default=5)
    max_tokens: int = Field(ge=1, le=32000, default=4096)
    temperature: float = Field(ge=0.0, le=2.0, default=0.7)
    system_prompt: str = ""
    context_source: ContextSource = ContextSource.api_request
    metadata: dict[str, Any] = Field(default_factory=dict)
    budget_remaining: int = Field(ge=0, default=10000)
    retry_count: int = Field(ge=0, default=0)
    fallback_providers: list[AIProviderType] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        from_attributes = True
        use_enum_values = True


class AIProviderContextDB(Model):
    """
    Tortoise ORM model for persisting AIProviderContext.

    Enables audit trail, metrics collection, and context recovery across
    service restarts.
    """

    id = fields.IntField(primary_key=True)
    request_id = fields.CharField(max_length=64, unique=True, db_index=True)
    session_id = fields.CharField(max_length=64, null=True, db_index=True)
    provider = fields.CharField(max_length=32, db_index=True)
    model = fields.CharField(max_length=128)
    priority = fields.IntField(default=5)
    max_tokens = fields.IntField(default=4096)
    temperature = fields.FloatField(default=0.7)
    system_prompt = fields.TextField(default="")
    context_source = fields.CharField(max_length=32, default="api_request")
    metadata_json = fields.JSONField(default={})
    budget_remaining = fields.IntField(default=10000)
    retry_count = fields.IntField(default=0)
    fallback_providers_json = fields.JSONField(default=[])
    created_at = fields.DatetimeField(auto_now_add=True, db_index=True)
    expires_at = fields.DatetimeField(null=True, db_index=True)
    updated_at = fields.DatetimeField(auto_now=True)
    completed_at = fields.DatetimeField(null=True)

    class Meta:
        """Tortoise ORM metadata."""

        table = "ai_provider_context"
        indexes = (
            ("request_id", "provider"),
            ("session_id", "created_at"),
            ("expires_at",),
        )

    async def to_context(self) -> AIProviderContext:
        """Convert DB model to runtime AIProviderContext."""
        return AIProviderContext(
            provider=AIProviderType(self.provider),
            model=self.model,
            request_id=self.request_id,
            session_id=self.session_id,
            priority=self.priority,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system_prompt=self.system_prompt,
            context_source=ContextSource(self.context_source),
            metadata=self.metadata_json,
            budget_remaining=self.budget_remaining,
            retry_count=self.retry_count,
            fallback_providers=[
                AIProviderType(p) for p in (self.fallback_providers_json or [])
            ],
            created_at=self.created_at,
            expires_at=self.expires_at,
        )

    @classmethod
    async def from_context(cls, context: AIProviderContext) -> AIProviderContextDB:
        """Create DB model from runtime AIProviderContext."""
        return cls(
            request_id=context.request_id,
            session_id=context.session_id,
            provider=context.provider.value,
            model=context.model,
            priority=context.priority,
            max_tokens=context.max_tokens,
            temperature=context.temperature,
            system_prompt=context.system_prompt,
            context_source=context.context_source.value,
            metadata_json=context.metadata,
            budget_remaining=context.budget_remaining,
            retry_count=context.retry_count,
            fallback_providers_json=[p.value for p in context.fallback_providers],
            created_at=context.created_at,
            expires_at=context.expires_at,
        )

    @classmethod
    async def get_or_create_from_context(
        cls, context: AIProviderContext
    ) -> tuple[AIProviderContextDB, bool]:
        """
        Get or create a DB record from context.

        Args:
            context: AIProviderContext instance

        Returns:
            Tuple of (db_instance, created_bool)
        """
        async with in_transaction():
            obj, created = await cls.get_or_create(
                request_id=context.request_id,
                defaults={
                    "session_id": context.session_id,
                    "provider": context.provider.value,
                    "model": context.model,
                    "priority": context.priority,
                    "max_tokens": context.max_tokens,
                    "temperature": context.temperature,
                    "system_prompt": context.system_prompt,
                    "context_source": context.context_source.value,
                    "metadata_json": context.metadata,
                    "budget_remaining": context.budget_remaining,
                    "retry_count": context.retry_count,
                    "fallback_providers_json": [p.value for p in context.fallback_providers],
                    "created_at": context.created_at,
                    "expires_at": context.expires_at,
                },
            )
            return obj, created

    @classmethod
    async def list_by_session(cls, session_id: str) -> list[AIProviderContextDB]:
        """
        List all contexts for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of AIProviderContextDB records
        """
        return await cls.filter(session_id=session_id).order_by("-created_at")

    @classmethod
    async def cleanup_expired(cls) -> int:
        """
        Delete expired contexts from database.

        Returns:
            Count of deleted records
        """
        now = datetime.utcnow()
        result = await cls.filter(expires_at__lte=now).delete()
        logger.info(f"Cleaned up {result} expired AI provider contexts")
        return result


class AIProviderMetrics(BaseModel):
    """Metrics for AI provider usage tracking."""

    request_id: str
    provider: AIProviderType
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    cost_cents: int = 0
    success: bool = True
    error_message: str | None = None
    retry_attempts: int = 0

    class Config:
        """Pydantic config."""

        use_enum_values = True
