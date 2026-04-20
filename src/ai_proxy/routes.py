"""
AI Proxy ASGI Routes — /v1/chat/completions, /v1/models, /v1/usage, /v1/tokens/count.

Drop-in OpenAI-compatible proxy with multi-provider routing, format
translation, rate limiting, and cost tracking.
"""
from __future__ import annotations

import logging
import time
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route, Router

from ai_proxy.providers.registry import (
    get_provider,
    get_enabled_providers,
    get_free_providers,
    list_all_models,
)
from ai_proxy.routing.combo import smart_route, ComboConfig, ComboTarget, Strategy, route_request
from ai_proxy.services.rate_limiter import rate_limiter
from ai_proxy.services.token_counter import token_counter
from ai_proxy.services.usage_tracker import usage_tracker
from ai_proxy.translators.core import openai_to_anthropic_request
from ai_proxy.api.batches import (
    create_batch,
    list_batches,
    get_batch,
    get_batch_results,
    cancel_batch,
)
from ai_proxy.api.files import (
    upload_file,
    list_files,
    get_file,
    delete_file,
)

logger = logging.getLogger("ai_proxy.routes")


# ── /v1/chat/completions ─────────────────────────────────────────────────────

async def chat_completions(request: Request) -> JSONResponse | StreamingResponse:
    """OpenAI-compatible chat completions endpoint with multi-provider routing."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            {"error": {"message": "Invalid JSON body", "type": "invalid_request_error"}},
            status_code=400,
        )

    model = body.get("model")
    if not model:
        return JSONResponse(
            {"error": {"message": "model is required", "type": "invalid_request_error"}},
            status_code=400,
        )

    stream = body.get("stream", False)

    # Check for X-Provider header to force a specific provider
    force_provider = request.headers.get("x-provider")
    # Check for cost optimization header
    prefer_free = request.headers.get("x-prefer-free", "").lower() in ("true", "1", "yes")
    max_cost_str = request.headers.get("x-max-cost-per-1k")
    max_cost = float(max_cost_str) if max_cost_str else None

    start = time.monotonic()

    if force_provider:
        # Direct provider routing
        provider = get_provider(force_provider)
        if not provider:
            return JSONResponse(
                {"error": {"message": f"Unknown provider: {force_provider}", "type": "invalid_request_error"}},
                status_code=400,
            )
        combo = ComboConfig(
            id=f"direct-{force_provider}",
            name=f"Direct to {provider.name}",
            strategy=Strategy.PRIORITY,
            targets=[ComboTarget(provider_id=provider.id, model_id=model)],
        )
        result = await route_request(body, combo, stream=stream)
    else:
        # Smart routing
        result = await smart_route(body, stream=stream, prefer_free=prefer_free, max_cost_per_1k=max_cost)

    latency = (time.monotonic() - start) * 1000

    # Update rate limiter from upstream headers
    if result.headers and result.provider_id:
        rate_limiter.update_from_headers(result.provider_id, result.headers)

    if not result.ok:
        error_body: dict[str, Any] = {
            "error": {
                "message": result.error or "Upstream provider error",
                "type": "upstream_error",
                "provider": result.provider_id,
                "model": result.model_id,
            }
        }
        return JSONResponse(error_body, status_code=result.status_code)

    # Streaming response
    if stream and result.stream:
        async def _stream_sse():
            async for chunk in result.stream:
                yield chunk

        # Track usage (approximate for streams)
        usage_tracker.record_from_response(
            provider_id=result.provider_id,
            model_id=result.model_id,
            response_body=None,
            latency_ms=latency,
            stream=True,
            request_id=result.request_id,
        )

        response_headers: dict[str, str] = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Provider": result.provider_id,
            "X-Model": result.model_id,
            "X-Latency-Ms": str(round(latency, 1)),
        }
        if result.request_id:
            response_headers["X-Request-Id"] = result.request_id

        return StreamingResponse(
            _stream_sse(),
            media_type="text/event-stream",
            headers=response_headers,
        )

    # JSON response
    if result.body:
        # Track usage from response
        provider = get_provider(result.provider_id)
        model_cfg = provider.get_model(result.model_id) if provider else None
        usage_tracker.record_from_response(
            provider_id=result.provider_id,
            model_id=result.model_id,
            response_body=result.body,
            latency_ms=latency,
            input_cost_per_1m=model_cfg.cost.input if model_cfg else 0,
            output_cost_per_1m=model_cfg.cost.output if model_cfg else 0,
            request_id=result.request_id,
        )

        # Add routing metadata
        result.body["_proxy"] = {
            "provider": result.provider_id,
            "model": result.model_id,
            "latency_ms": round(latency, 1),
        }

        json_headers: dict[str, str] = {
            "X-Provider": result.provider_id,
            "X-Model": result.model_id,
            "X-Latency-Ms": str(round(latency, 1)),
        }
        if result.request_id:
            json_headers["X-Request-Id"] = result.request_id

        return JSONResponse(result.body, headers=json_headers)

    return JSONResponse({"error": {"message": "Empty response from provider"}}, status_code=502)


# ── /v1/models ───────────────────────────────────────────────────────────────

async def list_models(request: Request) -> JSONResponse:
    """OpenAI-compatible model listing."""
    models = list_all_models()
    return JSONResponse({
        "object": "list",
        "data": models,
    })


# ── /v1/providers ────────────────────────────────────────────────────────────

async def list_providers(request: Request) -> JSONResponse:
    """List all configured providers with status."""
    providers = []
    for p in get_enabled_providers():
        providers.append({
            "id": p.id,
            "name": p.name,
            "format": p.api_format.value,
            "is_free": p.is_free,
            "models": len(p.models),
            "rate_limit": rate_limiter.get_status(p.id),
        })
    free = get_free_providers()
    return JSONResponse({
        "providers": providers,
        "total": len(providers),
        "free_available": len(free),
    })


# ── /v1/usage ────────────────────────────────────────────────────────────────

async def usage_summary(request: Request) -> JSONResponse:
    """Return usage summary and recent activity."""
    return JSONResponse({
        "summary": usage_tracker.get_summary(),
        "recent": usage_tracker.get_recent(limit=20),
        "rate_limits": rate_limiter.get_all_status(),
    })


# ── /v1/cost ─────────────────────────────────────────────────────────────────

async def cost_report(request: Request) -> JSONResponse:
    """Detailed cost breakdown by provider and model."""
    summary = usage_tracker.get_summary()
    return JSONResponse({
        "total_cost_usd": summary["total_cost_usd"],
        "total_tokens": summary["total_tokens"],
        "total_requests": summary["total_requests"],
        "by_provider": summary["by_provider"],
    })


# ── /v1/tokens/count ─────────────────────────────────────────────────────────

async def count_tokens(request: Request) -> JSONResponse:
    """
    Count tokens for a request without sending it (Anthropic-only).

    Accepts an OpenAI-format body; translates to Anthropic format before counting.
    Response: {"input_tokens": N, "model": "...", "provider": "..."}
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            {"error": {"message": "Invalid JSON body", "type": "invalid_request_error"}},
            status_code=400,
        )

    model = body.get("model", "")
    if not model:
        return JSONResponse(
            {"error": {"message": "model is required", "type": "invalid_request_error"}},
            status_code=400,
        )

    # Translate OpenAI → Anthropic format for counting
    anthropic_body = openai_to_anthropic_request(body)
    messages = anthropic_body.get("messages", [])
    system = anthropic_body.get("system")
    tools = anthropic_body.get("tools")

    # Allow caller to specify provider; default to 'anthropic'
    provider_id = request.headers.get("x-provider", "anthropic")

    input_tokens = await token_counter.count(
        model=model,
        messages=messages,
        system=system,
        tools=tools,
        provider_id=provider_id,
    )

    if input_tokens is None:
        return JSONResponse(
            {"error": {"message": "Token counting unavailable for this provider", "type": "not_supported"}},
            status_code=501,
        )

    return JSONResponse({
        "input_tokens": input_tokens,
        "model": model,
        "provider": provider_id,
    })


# ── Router ───────────────────────────────────────────────────────────────────

def create_proxy_router() -> Router:
    """Create the /v1/ API router."""
    return Router(routes=[
        Route("/chat/completions", chat_completions, methods=["POST"]),
        Route("/models", list_models, methods=["GET"]),
        Route("/providers", list_providers, methods=["GET"]),
        Route("/usage", usage_summary, methods=["GET"]),
        Route("/cost", cost_report, methods=["GET"]),
        Route("/tokens/count", count_tokens, methods=["POST"]),
        # Message Batches (Anthropic-native, 50% cost discount for async workloads)
        Route("/messages/batches", list_batches, methods=["GET"]),
        Route("/messages/batches", create_batch, methods=["POST"]),
        Route("/messages/batches/{batch_id}", get_batch, methods=["GET"]),
        Route("/messages/batches/{batch_id}/results", get_batch_results, methods=["GET"]),
        Route("/messages/batches/{batch_id}/cancel", cancel_batch, methods=["POST"]),
        # Files API (Anthropic beta — upload once, reference by file_id)
        Route("/files", list_files, methods=["GET"]),
        Route("/files", upload_file, methods=["POST"]),
        Route("/files/{file_id}", get_file, methods=["GET"]),
        Route("/files/{file_id}", delete_file, methods=["DELETE"]),
    ])

