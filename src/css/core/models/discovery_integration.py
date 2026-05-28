"""Integrate model discovery providers into ModelRegistry at startup.

Called from ASGI app lifespan to register async provider discovery functions.
Each provider is registered with a configurable cache TTL.
"""

import logging

from .registry import get_model_registry
from .discovery import (
    discover_openrouter_models,
    discover_ollama_models,
    discover_mistral_models,
    discover_groq_models,
)

logger = logging.getLogger(__name__)


async def register_model_discovery_providers() -> None:
    """Register all available model discovery providers with ModelRegistry.

    Called at app startup. Each provider is registered with an async discovery
    function and a cache TTL. Providers are discovered asynchronously on-demand,
    with automatic cache invalidation.

    Provider cache TTLs:
    - OpenRouter: 3600s (1 hour) — frequently updated catalog
    - Mistral: 7200s (2 hours) — stable API
    - Groq: 7200s (2 hours) — stable API
    - Ollama: 300s (5 minutes) — local; may change frequently
    """
    registry = get_model_registry()

    # OpenRouter: comprehensive multi-provider catalog
    # Updated frequently to reflect price/model changes
    registry.register_discovery(
        "openrouter",
        discover_openrouter_models,
        ttl_seconds=3600,
    )
    logger.debug("Registered OpenRouter model discovery (TTL: 3600s)")

    # Mistral: native API
    # Stable model list; less frequent updates
    registry.register_discovery(
        "mistral",
        discover_mistral_models,
        ttl_seconds=7200,
    )
    logger.debug("Registered Mistral model discovery (TTL: 7200s)")

    # Groq: ultra-fast inference
    # Stable model list; performance-focused
    registry.register_discovery(
        "groq",
        discover_groq_models,
        ttl_seconds=7200,
    )
    logger.debug("Registered Groq model discovery (TTL: 7200s)")

    # Ollama: local model runner
    # Frequently changes (new models added/removed locally)
    # Graceful timeout if Ollama is not running
    registry.register_discovery(
        "ollama",
        discover_ollama_models,
        ttl_seconds=300,
    )
    logger.debug("Registered Ollama model discovery (TTL: 300s)")

    logger.info("Model discovery providers registered: openrouter, mistral, groq, ollama")

