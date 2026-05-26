"""OpenRouter per-generation cost tracking and attribution.

Captures generation IDs from responses and fetches cost attribution
asynchronously for telemetry enrichment.
"""

import asyncio
from typing import Any

import aiohttp

from css.core.events.emitter import emit_event
from css.core.logger import getLogger


logger = getLogger(__name__)

# OpenRouter API endpoints for cost attribution
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"


def capture_generation_id(response_headers: dict[str, str]) -> str | None:
    """Extract generation ID from response headers.

    OpenRouter returns the generation ID in the 'x-request-id' or
    similar header. This ID is used to fetch cost attribution later.

    Args:
        response_headers: HTTP response headers from OpenRouter API

    Returns:
        Generation ID if found, None otherwise
    """
    # OpenRouter returns request-id in headers
    gen_id = response_headers.get("x-request-id")
    if gen_id:
        return gen_id

    # Fallback to other common header names
    for header_name in ["request-id", "generation-id", "x-generation-id"]:
        if header_name in response_headers:
            return response_headers[header_name]

    return None


async def fetch_cost_attribution(
    generation_id: str,
    api_key: str,
    model_id: str,
    timeout_seconds: int = 5,
) -> dict[str, Any] | None:
    """Fetch cost attribution for a completed generation.

    Calls OpenRouter's attribution API asynchronously to get cost info.
    Failures are logged but do not raise exceptions.

    Args:
        generation_id: Request/generation ID from response
        api_key: OpenRouter API key for authentication
        model_id: Model ID used for the generation
        timeout_seconds: Request timeout in seconds

    Returns:
        Attribution dict with cost_usd, actual_provider, etc. or None on error
    """
    if not generation_id:
        return None

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {api_key}",
            }
            # OpenRouter provides cost info via a GET endpoint or in the response itself
            # The generation ID allows querying completion info
            url = f"{OPENROUTER_API_BASE}/generation/{generation_id}"

            async with session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout_seconds),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "cost_usd": data.get("total_cost"),
                        "actual_provider": data.get("model"),
                        "generation_id": generation_id,
                    }
                else:
                    logger.debug(
                        f"Cost attribution fetch failed for {generation_id}: HTTP {resp.status}"
                    )
    except asyncio.TimeoutError:
        logger.debug(f"Cost attribution fetch timeout for {generation_id}")
    except Exception as e:
        logger.debug(f"Cost attribution fetch error for {generation_id}: {e}")

    return None


async def emit_cost_tracking_event(
    generation_id: str | None,
    model_id: str,
    api_key: str,
    cost_usd: float | None = None,
    actual_provider: str | None = None,
) -> None:
    """Emit cost tracking event asynchronously without blocking response.

    Spawns a fire-and-forget task to fetch cost attribution and emit events.
    Failures are logged but do not propagate.

    Args:
        generation_id: Request/generation ID from response
        model_id: Model ID used for the generation
        api_key: OpenRouter API key
        cost_usd: Optional direct cost from response
        actual_provider: Optional provider name from response
    """
    if not generation_id:
        return

    try:
        # Fire-and-forget: create task without awaiting
        # This allows the response to be returned immediately
        asyncio.create_task(
            _emit_cost_event_async(
                generation_id,
                model_id,
                api_key,
                cost_usd,
                actual_provider,
            )
        )
    except RuntimeError:
        logger.debug("Cannot create async task for cost tracking (no running event loop)")


async def _emit_cost_event_async(
    generation_id: str,
    model_id: str,
    api_key: str,
    cost_usd: float | None = None,
    actual_provider: str | None = None,
) -> None:
    """Internal async function to fetch and emit cost events.

    Args:
        generation_id: Request/generation ID
        model_id: Model ID
        api_key: OpenRouter API key
        cost_usd: Optional direct cost
        actual_provider: Optional provider name
    """
    try:
        # If cost is already in the response, use it directly
        if cost_usd is not None and actual_provider is not None:
            await emit_event(
                "openrouter.generation.cost_tracked",
                {
                    "generation_id": generation_id,
                    "model_id": model_id,
                    "cost_usd": cost_usd,
                    "actual_provider": actual_provider,
                    "source": "response_header",
                },
            )
            return

        # Fetch attribution from OpenRouter API
        attribution = await fetch_cost_attribution(
            generation_id,
            api_key,
            model_id,
        )

        if attribution:
            await emit_event(
                "openrouter.generation.cost_tracked",
                {
                    "generation_id": attribution.get("generation_id"),
                    "model_id": model_id,
                    "cost_usd": attribution.get("cost_usd"),
                    "actual_provider": attribution.get("actual_provider"),
                    "source": "attribution_api",
                },
            )
        else:
            await emit_event(
                "openrouter.generation.cost_tracking_failed",
                {
                    "generation_id": generation_id,
                    "model_id": model_id,
                    "reason": "attribution_fetch_failed",
                },
            )
    except Exception as e:
        logger.debug(f"Error emitting cost tracking event: {e}")


__all__ = [
    "capture_generation_id",
    "fetch_cost_attribution",
    "emit_cost_tracking_event",
]
