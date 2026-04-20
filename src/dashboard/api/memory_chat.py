"""Memory-enhanced chat endpoint — uses BetaAsyncObsidianMemoryTool via tool_runner."""
from __future__ import annotations

import json
import logging
import os
from typing import AsyncIterator

import anthropic
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

logger = logging.getLogger("dashboard.api.memory_chat")

_MEMORY_BETA = "memory-2025-08-18"
_DEFAULT_MODEL = "claude-opus-4-5"


def _get_client() -> tuple[anthropic.AsyncAnthropic | None, str | None]:
    """Return (client, error). Uses ANTHROPIC_API_KEY or provider registry."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        try:
            from ai_proxy.providers.registry import get_provider
            p = get_provider("anthropic")
            if p:
                api_key = p.get_api_key()
        except Exception:
            pass
    if not api_key:
        return None, "No Anthropic API key configured (set ANTHROPIC_API_KEY)"
    return anthropic.AsyncAnthropic(api_key=api_key), None


def _make_tool(vault_path: str) -> object:
    try:
        from memory.backends.obsidian_async import BetaAsyncObsidianMemoryTool
        return BetaAsyncObsidianMemoryTool(vault_path=vault_path)
    except ImportError:
        logger.warning("obsidian_async not available; falling back to builtin memory tool")
        try:
            from anthropic.lib.tools._beta_builtin_memory_tool import BetaAsyncBuiltinMemoryTool  # type: ignore[attr-defined]
            return BetaAsyncBuiltinMemoryTool()
        except ImportError:
            return None


async def api_memory_chat(request: Request) -> JSONResponse | StreamingResponse:
    """
    POST /api/proxy/memory-chat

    Body:
        messages      list   required  Anthropic message array
        model         str    optional  defaults to claude-opus-4-5
        system        str    optional  system prompt
        max_tokens    int    optional  defaults to 4096
        stream        bool   optional  if true, returns SSE stream
        vault_path    str    optional  override CYBERSEC_VAULT_PATH

    Returns final Anthropic Message JSON (or SSE stream of events).
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    messages = body.get("messages")
    if not messages:
        return JSONResponse({"error": "'messages' is required"}, status_code=400)

    model = body.get("model", _DEFAULT_MODEL)
    system = body.get("system")
    max_tokens = int(body.get("max_tokens", 4096))
    do_stream = bool(body.get("stream", False))
    vault_path = body.get("vault_path") or os.getenv("CYBERSEC_VAULT_PATH", "./data/vault")

    client, err = _get_client()
    if err:
        return JSONResponse({"error": err}, status_code=400)

    memory_tool = _make_tool(vault_path)
    if memory_tool is None:
        return JSONResponse({"error": "memory tool not available"}, status_code=500)

    runner_kwargs: dict = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "tools": [memory_tool],
        "betas": [_MEMORY_BETA],
    }
    if system:
        runner_kwargs["system"] = system

    try:
        if do_stream:
            return StreamingResponse(
                _stream_events(client, runner_kwargs),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
            )

        runner = client.beta.messages.tool_runner(**runner_kwargs)
        final = await runner.until_done()
        return JSONResponse(final.model_dump())

    except anthropic.AuthenticationError:
        return JSONResponse({"error": "Anthropic authentication failed"}, status_code=401)
    except anthropic.RateLimitError:
        return JSONResponse({"error": "Rate limited by Anthropic"}, status_code=429)
    except anthropic.APIError as exc:
        return JSONResponse({"error": str(exc)}, status_code=502)
    except Exception as exc:
        logger.exception("memory_chat error")
        return JSONResponse({"error": str(exc)}, status_code=500)
    finally:
        await client.close()


async def _stream_events(client: anthropic.AsyncAnthropic, kwargs: dict) -> AsyncIterator[bytes]:
    try:
        runner = client.beta.messages.tool_runner(**{**kwargs, "stream": True})
        async for event in runner:
            data = json.dumps(
                event.model_dump(exclude_unset=True) if hasattr(event, "model_dump") else {"event": str(event)},
                separators=(",", ":"),
            )
            yield f"data: {data}\n\n".encode()
        yield b"data: [DONE]\n\n"
    except Exception as exc:
        yield f"data: {json.dumps({'error': str(exc)})}\n\n".encode()
