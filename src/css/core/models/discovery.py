"""Dynamic model discovery for LLM providers.

Provides async functions that fetch fresh model catalogs from provider APIs.
These are registered with ModelRegistry via register_discovery() at startup.

Each discovery function:
1. Fetches the latest model list from the provider API
2. Returns list[ModelMetadata] with current pricing, capabilities
3. Handles errors gracefully (logged, no exception propagation)
4. Uses cache TTL to avoid excessive re-fetching (configurable per provider)

Discovery functions are async callables with signature:
    async def discover_provider(...) -> list[ModelMetadata]

Pattern: Register at app startup, invoke via registry.discover_models(provider).
"""

import asyncio
import logging
from typing import Optional, Any

import aiohttp

from .models import ModelMetadata, ModelPricing
from .enums import ModelCapability, ModelProvider, ModelFamily

logger = logging.getLogger(__name__)


async def discover_openrouter_models() -> list[ModelMetadata]:
    """Fetch available models from OpenRouter API.

    Returns list of ModelMetadata for all models in the OpenRouter catalog.
    Handles API errors gracefully — returns empty list on failure.

    OpenRouter endpoint: GET https://openrouter.ai/api/v1/models
    Returns: { data: [{ id, name, pricing, ... }, ...] }
    """
    url = "https://openrouter.ai/api/v1/models"
    models: list[ModelMetadata] = []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    logger.warning(
                        f"OpenRouter discovery failed: HTTP {resp.status}",
                    )
                    return models

                data = await resp.json()
                if not isinstance(data, dict) or "data" not in data:
                    logger.warning("OpenRouter discovery: unexpected response format")
                    return models

                for item in data.get("data", []):
                    try:
                        model = _parse_openrouter_model(item)
                        if model:
                            models.append(model)
                    except Exception as e:
                        logger.debug(
                            f"OpenRouter: failed to parse model {item.get('id')}: {e}",
                        )
                        continue

    except asyncio.TimeoutError:
        logger.warning("OpenRouter discovery: request timeout")
    except Exception as e:
        logger.warning(f"OpenRouter discovery failed: {e}")

    return models


def _parse_openrouter_model(item: dict[str, Any]) -> Optional[ModelMetadata]:
    """Parse a single OpenRouter model entry into ModelMetadata.

    Returns None if model data is invalid or incomplete.
    """
    model_id = item.get("id")
    if not model_id:
        return None

    display_name = item.get("name", model_id)
    description = item.get("description", "")

    # Extract pricing
    pricing_data = item.get("pricing", {})
    input_cost = pricing_data.get("prompt")  # per 1k tokens
    output_cost = pricing_data.get("completion")  # per 1k tokens

    if input_cost is None or output_cost is None:
        return None

    # Infer capabilities from model name/description
    capabilities = _infer_openrouter_capabilities(model_id, display_name, description)

    # Map OpenRouter model families to ModelFamily
    family = _infer_openrouter_family(model_id, display_name)
    
    # Map OpenRouter model families to ModelProvider
    provider = _get_openrouter_provider(model_id)
    if not provider:
        return None

    pricing = ModelPricing(
        input_tokens_per_1k=input_cost,
        output_tokens_per_1k=output_cost,
    )

    return ModelMetadata(
        id=model_id,
        provider=provider,
        family=family,
        display_name=display_name,
        context_window=item.get("context_length", 128000),
        max_output_tokens=item.get("max_output_tokens", 4096),
        latency_ms=item.get("latency_ms", 500),
        pricing=pricing,
        capabilities=capabilities,
    )


def _infer_openrouter_capabilities(
    model_id: str, name: str, description: str
) -> set[ModelCapability]:
    """Infer ModelCapability flags from OpenRouter model metadata."""
    capabilities = set()
    lower_id = model_id.lower()
    lower_desc = description.lower()

    if any(x in lower_id for x in ["vision", "gpt-4v", "o1", "o3"]):
        capabilities.add(ModelCapability.VISION)

    if any(x in lower_id for x in ["o1", "o3", "reasoning", "deepseek-r1"]):
        capabilities.add(ModelCapability.EXTENDED_THINKING)

    if "function" in lower_desc or "tool" in lower_desc:
        capabilities.add(ModelCapability.FUNCTION_CALLING)

    return capabilities


def _infer_openrouter_family(model_id: str, name: str) -> ModelFamily:
    """Infer ModelFamily from OpenRouter model ID and name."""
    lower_id = model_id.lower()
    
    if "claude" in lower_id:
        return ModelFamily.CLAUDE
    elif "gpt" in lower_id:
        return ModelFamily.GPT
    elif "gemini" in lower_id:
        return ModelFamily.GEMINI
    elif "llama" in lower_id:
        return ModelFamily.LLAMA
    elif "mistral" in lower_id:
        return ModelFamily.MISTRAL_MODEL
    elif "deepseek" in lower_id:
        return ModelFamily.DEEPSEEK_MODEL
    else:
        return ModelFamily.OPEN_SOURCE


def _get_openrouter_provider(model_id: str) -> Optional[ModelProvider]:
    """Map OpenRouter model ID prefix to ModelProvider.

    E.g., "openai/gpt-4o" → ModelProvider.OPENAI
    """
    prefix = model_id.split("/")[0].lower() if "/" in model_id else ""

    provider_map: dict[str, str] = {
        "openai": "openai",
        "anthropic": "anthropic",
        "deepseek": "deepseek",
        "mistral": "mistral",
        "google": "google",
        "meta": "meta",
        "xai": "xai",
        "cohere": "cohere",
        "perplexity": "perplexity",
    }

    provider_slug = provider_map.get(prefix)
    if not provider_slug:
        return None

    # Convert slug to ModelProvider enum value
    try:
        return ModelProvider(provider_slug)
    except (ValueError, KeyError):
        return None


async def discover_ollama_models() -> list[ModelMetadata]:
    """Fetch available models from a local Ollama instance.

    Ollama API endpoint: GET http://localhost:11434/api/tags
    Returns: { models: [{ name, modified_at, size, ... }, ...] }
    """
    url = "http://localhost:11434/api/tags"
    models: list[ModelMetadata] = []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    logger.debug(f"Ollama discovery failed: HTTP {resp.status}")
                    return models

                data = await resp.json()
                if not isinstance(data, dict) or "models" not in data:
                    logger.debug("Ollama discovery: unexpected response format")
                    return models

                for item in data.get("models", []):
                    try:
                        model = _parse_ollama_model(item)
                        if model:
                            models.append(model)
                    except Exception as e:
                        logger.debug(f"Ollama: failed to parse model {item.get('name')}: {e}")
                        continue

    except asyncio.TimeoutError:
        logger.debug("Ollama discovery: request timeout (Ollama may not be running)")
    except Exception as e:
        logger.debug(f"Ollama discovery failed: {e}")

    return models


def _parse_ollama_model(item: dict[str, Any]) -> Optional[ModelMetadata]:
    """Parse a single Ollama model entry into ModelMetadata."""
    model_id = item.get("name")
    if not model_id:
        return None

    # Ollama models have simple structure; infer from name
    display_name = model_id
    capabilities = _infer_ollama_capabilities(model_id)

    # All Ollama models are "local" until we have better mapping
    family = ModelFamily.OPEN_SOURCE

    return ModelMetadata(
        id=f"ollama/{model_id}",
        provider=ModelProvider("ollama"),
        family=family,
        display_name=f"Ollama: {display_name}",
        context_window=item.get("context_window", 2048),
        max_output_tokens=item.get("max_output_tokens", 256),
        latency_ms=item.get("latency_ms", 1000),
        pricing=None,  # Local models have no cost
        capabilities=capabilities,
    )


def _infer_ollama_capabilities(model_id: str) -> set[ModelCapability]:
    """Infer capabilities from Ollama model name."""
    capabilities = set()
    lower_id = model_id.lower()

    if "vision" in lower_id or "llava" in lower_id:
        capabilities.add(ModelCapability.VISION)

    capabilities.add(ModelCapability.STREAMING)
    return capabilities


async def discover_mistral_models() -> list[ModelMetadata]:
    """Fetch available models from Mistral API.

    Mistral endpoint: GET https://api.mistral.ai/v1/models
    Returns: { object: "list", data: [{ id, object, owned_by, ... }, ...] }
    """
    url = "https://api.mistral.ai/v1/models"
    models: list[ModelMetadata] = []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    logger.debug(f"Mistral discovery failed: HTTP {resp.status}")
                    return models

                data = await resp.json()
                if not isinstance(data, dict) or "data" not in data:
                    logger.debug("Mistral discovery: unexpected response format")
                    return models

                for item in data.get("data", []):
                    try:
                        model = _parse_mistral_model(item)
                        if model:
                            models.append(model)
                    except Exception as e:
                        logger.debug(f"Mistral: failed to parse model {item.get('id')}: {e}")
                        continue

    except asyncio.TimeoutError:
        logger.debug("Mistral discovery: request timeout")
    except Exception as e:
        logger.debug(f"Mistral discovery failed: {e}")

    return models


def _parse_mistral_model(item: dict[str, Any]) -> Optional[ModelMetadata]:
    """Parse a single Mistral model entry into ModelMetadata."""
    model_id = item.get("id")
    if not model_id:
        return None

    display_name = model_id
    family = ModelFamily.MISTRAL_MODEL
    capabilities = set()

    # Mistral doesn't include pricing in API; use defaults
    return ModelMetadata(
        id=model_id,
        provider=ModelProvider("mistral"),
        family=family,
        display_name=display_name,
        context_window=item.get("context_window", 32768),
        max_output_tokens=item.get("max_output_tokens", 4096),
        latency_ms=item.get("latency_ms", 300),
        capabilities=capabilities,
    )


async def discover_groq_models() -> list[ModelMetadata]:
    """Fetch available models from Groq API.

    Groq endpoint: GET https://api.groq.com/openai/v1/models
    Returns: { object: "list", data: [{ id, object, owned_by, ... }, ...] }
    """
    url = "https://api.groq.com/openai/v1/models"
    models: list[ModelMetadata] = []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    logger.debug(f"Groq discovery failed: HTTP {resp.status}")
                    return models

                data = await resp.json()
                if not isinstance(data, dict) or "data" not in data:
                    logger.debug("Groq discovery: unexpected response format")
                    return models

                for item in data.get("data", []):
                    try:
                        model = _parse_groq_model(item)
                        if model:
                            models.append(model)
                    except Exception as e:
                        logger.debug(f"Groq: failed to parse model {item.get('id')}: {e}")
                        continue

    except asyncio.TimeoutError:
        logger.debug("Groq discovery: request timeout")
    except Exception as e:
        logger.debug(f"Groq discovery failed: {e}")

    return models


def _parse_groq_model(item: dict[str, Any]) -> Optional[ModelMetadata]:
    """Parse a single Groq model entry into ModelMetadata."""
    model_id = item.get("id")
    if not model_id:
        return None

    display_name = model_id
    capabilities = set()
    capabilities.add(ModelCapability.STREAMING)

    return ModelMetadata(
        id=model_id,
        provider=ModelProvider("groq"),
        family=ModelFamily.OPEN_SOURCE,
        display_name=display_name,
        context_window=item.get("context_window", 8192),
        max_output_tokens=item.get("max_output_tokens", 4096),
        latency_ms=item.get("latency_ms", 100),
        capabilities=capabilities,
    )


__all__ = [
    "discover_openrouter_models",
    "discover_ollama_models",
    "discover_mistral_models",
    "discover_groq_models",
]
