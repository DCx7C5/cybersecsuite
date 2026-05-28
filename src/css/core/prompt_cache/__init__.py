"""Prompt caching orchestration layer (Phase 11).

Multi-tier caching strategy:
  1. Exact-match cache (Redis) — all providers, O(1) lookup
  2. Provider-native cache — Anthropic/OpenAI/DeepSeek, managed per-request
  3. Resource cache (deferred) — Gemini cachedContent, explicit lifecycle

Architecture:
  - CachingCapability enum: Provider capability discovery
  - PromptCacheManager: Multi-tier orchestration
  - Tier 1 (Exact): Redis exact-match via L2RedisCache
  - Tier 2 (Native): Provider-native via adapter.cache_capability
  - Tier 3 (Resource): Explicit resource creation (Phase 12+)

Integration points:
  - css.core.sdks.css_client.CSSLLMClient.call() uses PromptCacheManager
  - Adapters (src/css/core/sdks/adapters/*.py) expose cache_capability property
  - Metrics → OpenObserve (cache hits, cost savings, native usage)
"""

from .anthropic_breakpoints import inject_cache_breakpoints, estimate_message_tokens
from .cost_savings_tracker import CostSavingsTracker
from .exact_match_cache import ExactMatchPromptCache
from .manager import PromptCacheManager
from .metrics_exporter import OpenObserveMetricsExporter, CacheMetricsCollector
from .native_cache_tracking import NativeCacheTracker, NativeCacheDetector
from .streaming_buffer import StreamingBuffer, PromptCacheStreamingBuffer
from .types import (
    CachingCapability,
    CacheCapabilityMetadata,
    ResponseCacheStats,
)
