"""
Live Models API — query Anthropic for available models in real time.

Routes:
  GET /v1/models/live               — list all models from Anthropic's API
  GET /v1/models/live/{model_id}    — retrieve a specific model's metadata
"""


import logging
from typing import Any

import anthropic
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.registries.providers import get_provider

logger = logging.getLogger("ai_proxy.models")


def _get_client(provider_id: str = "anthropic") -> anthropic.AsyncAnthropic | None:
    provider = get_provider(provider_id)
    if not provider:
        return None
    api_key = provider.get_api_key()
    if not api_key:
        return None
    return anthropic.AsyncAnthropic(
        api_key=api_key,
        base_url=provider.base_url,
        max_retries=2,
    )


async def list_models_live(request: Request) -> JSONResponse:
    """
    GET /v1/models/live

    Returns live model listing from Anthropic's API.
    Supports pagination via ?after_id= and ?limit= query params.
    """
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        limit_str = request.query_params.get("limit", "100")
        after_id = request.query_params.get("after_id")
        before_id = request.query_params.get("before_id")

        kwargs: dict[str, Any] = {"limit": int(limit_str)}
        if after_id:
            kwargs["after_id"] = after_id
        if before_id:
            kwargs["before_id"] = before_id

        models: list[dict[str, Any]] = []
        async for model in client.models.list(**kwargs):
            models.append(model.model_dump())

        return JSONResponse({
            "object": "list",
            "data": models,
            "count": len(models),
        })
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()


async def get_model_live(request: Request) -> JSONResponse:
    """GET /v1/models/live/{model_id} — retrieve a specific model's metadata from Anthropic."""
    model_id: str = request.path_params["model_id"]
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        model = await client.models.retrieve(model_id)
        return JSONResponse(model.model_dump())
    except anthropic.NotFoundError:
        return JSONResponse({"error": {"message": f"Model {model_id!r} not found"}}, status_code=404)
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()
