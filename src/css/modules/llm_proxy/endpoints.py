"""OpenAI-compatible local LLM proxy endpoints."""

import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

router = APIRouter(prefix="/v1", tags=["llm-proxy"])


def _extract_prompt(messages: list[dict[str, Any]]) -> str:
    for message in reversed(messages):
        if message.get("role") != "user":
            continue
        content = message.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            chunks = [str(chunk.get("text", "")) for chunk in content if isinstance(chunk, dict)]
            return " ".join(part for part in chunks if part)
    return ""


def _parse_provider_model(payload: dict[str, Any]) -> tuple[str, str]:
    provider = str(payload.get("provider", "")).strip()
    model = str(payload.get("model", "")).strip()
    if not provider and "/" in model:
        provider, model = model.split("/", 1)
    if not provider:
        provider = "ollama"
    if not model:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="model is required")
    return provider, model


@router.get("/health")
async def llm_proxy_health() -> dict[str, str]:
    return {"status": "ok", "component": "llm_proxy"}


@router.get("/models")
async def list_models(
    provider: str | None = Query(None),
    capability: str | None = Query(None),
    tag: str | None = Query(None),
    tags: str | None = Query(None),
    match_all_tags: bool = Query(False),
) -> dict[str, Any]:
    from css.core.models import ModelCapability, get_model_registry

    capability_filter: ModelCapability | None = None
    if capability is not None:
        try:
            capability_filter = ModelCapability(capability.strip().lower())
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"invalid capability: {capability}",
            ) from exc

    tag_filters = [item.strip() for item in tags.split(",") if item.strip()] if tags else None
    provider_filter = provider.strip() if isinstance(provider, str) else None
    tag_filter = tag.strip() if isinstance(tag, str) else None

    registry = get_model_registry()
    await registry.sync_from_catalog(clear_existing=False)
    models = registry.list_models(
        provider=provider_filter,
        capability=capability_filter,
        tag=tag_filter,
        tags=tag_filters,
        match_all_tags=match_all_tags,
    )

    data: list[dict[str, str | list[str]]] = []
    for metadata in models:
        owned_by = str(metadata.provider.value)
        model_id = metadata.id if "/" in metadata.id else f"{owned_by}/{metadata.id}"
        data.append(
            {
                "id": model_id,
                "object": "model",
                "owned_by": owned_by,
                "tags": metadata.tags,
            }
        )
    return {"object": "list", "data": data}


@router.post("/chat/completions")
async def create_chat_completion(payload: dict[str, Any]) -> dict[str, Any]:
    from .client import UnifiedLLMClient

    if payload.get("stream"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="stream=true is not yet supported by the local proxy",
        )

    provider, model = _parse_provider_model(payload)
    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="messages must be a non-empty list",
        )

    client = UnifiedLLMClient()
    started = time.time()
    try:
        result = await client.complete(
            messages=messages,
            combo_id=payload.get("combo_id"),
            provider=provider,
            model=model,
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"provider request failed: {exc}") from exc

    completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
    created = int(started)
    finish_reason = result.stop_reason if result.stop_reason else "stop"
    return {
        "id": completion_id,
        "object": "chat.completion",
        "created": created,
        "model": f"{provider}/{model}",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": result.response},
                "finish_reason": finish_reason,
            }
        ],
        "usage": {
            "prompt_tokens": result.input_tokens,
            "completion_tokens": result.output_tokens,
            "total_tokens": result.input_tokens + result.output_tokens,
        },
    }
