"""Runtime types for prompt caching layer."""

from datetime import UTC, datetime
from enum import Enum
from typing import TypedDict

import msgspec


class CachingCapability(str, Enum):
    """Enum defining prompt caching capabilities per provider adapter."""

    NONE = "none"
    """No caching support (fallback for unsupported providers)."""

    EXACT_ONLY = "exact_only"
    """Exact input match required; provider-agnostic Redis cache."""

    NATIVE_AUTOMATIC = "native_automatic"
    """Provider-native automatic caching (Anthropic, OpenAI, DeepSeek).
    Manager auto-enables on supported models."""

    NATIVE_AUTOMATIC_WITH_EXPLICIT_BREAKPOINTS = "native_automatic_with_explicit_breakpoints"
    """Provider supports explicit cache breakpoints (Anthropic).
    Manager can inject cache control tokens for fine-grained control."""

    NATIVE_RESOURCE = "native_resource"
    """Provider supports cached resources (Gemini cachedContent).
    Requires explicit resource creation + management (deferred to Phase 12)."""


class CacheCapabilityMetadata(TypedDict, total=False):
    """Adapter-provided metadata about prompt caching capabilities."""

    capability: CachingCapability
    """What caching strategy this adapter supports."""

    supports_cache_control: bool
    """Whether adapter supports explicit cache control tokens (e.g., Anthropic)."""

    supports_cache_creation: bool
    """Whether adapter supports explicit cache/resource creation (e.g., Gemini)."""

    estimated_cache_cost_ratio: float
    """Estimated cost ratio (cached vs uncached) if available, e.g., 0.1 for Anthropic."""

    cache_ttl_seconds: int | None
    """Default cache TTL in seconds, if applicable."""

    max_cache_size_tokens: int | None
    """Maximum cache size per request, if applicable."""


class ResponseCacheStats(msgspec.Struct, frozen=True, kw_only=True):
    """Response-level prompt cache metrics for a single LLM call.

    Tracks where cached content came from (exact-match Redis vs provider-native)
    and estimated cost savings.
    """

    exact_match_hit: bool = False
    """Response retrieved from exact-match Redis cache (Tier 1)."""

    native_cache_hit: bool = False
    """Response used provider-native cache (Tier 2, no re-encoding needed)."""

    native_cache_created: bool = False
    """Response created a new provider-native cache entry."""

    input_tokens_cached: int = 0
    """Tokens from provider cache (not billed if cached)."""

    input_tokens_uncached: int = 0
    """Fresh input tokens billed at full rate."""

    output_tokens: int = 0
    """Output tokens always billed (not cached)."""

    estimated_savings_usd: float = 0.0
    """Estimated USD savings from caching vs uncached call."""

    cache_key_hash: str | None = None
    """Hash of exact-match Redis key if exact_match_hit=True."""

    created_at: datetime = msgspec.field(default_factory=lambda: datetime.now(UTC))
    """Timestamp when stats were recorded."""

