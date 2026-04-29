"""Extended thinking tool — invoke Claude with thinking enabled for deep forensic analysis.

Uses the Anthropic SDK `thinking={"type":"enabled","budget_tokens":...}` parameter
to expose Claude's reasoning chain alongside the final answer.
"""
from __future__ import annotations

import os
from typing import Any

from ..sdk_compat import tool
from ..helpers import JsonDict, sdk_result, sdk_error


@tool(
    "invoke_with_thinking",
    "Run a forensic query with Claude's extended thinking enabled. Returns reasoning chain + answer.",
    {
        "prompt": {"type": "string", "description": "The question or task requiring deep reasoning"},
        "budget_tokens": {
            "type": "integer",
            "description": "Max tokens for thinking (default 8000, min 1024, max 32000)",
            "default": 8000,
        },
        "model": {
            "type": "string",
            "description": "Model to use (must support extended thinking, e.g. claude-sonnet-4-5-20250929)",
            "default": "claude-sonnet-4-5-20250929",
        },
        "system": {"type": "string", "description": "Optional system prompt"},
        "max_tokens": {
            "type": "integer",
            "description": "Max output tokens (default 16000)",
            "default": 16000,
        },
        "include_thinking": {
            "type": "boolean",
            "description": "Include the thinking blocks in the response (default true)",
            "default": True,
        },
    },
)
async def invoke_with_thinking(args: dict[str, Any]) -> JsonDict:
    prompt = str(args.get("prompt", "")).strip()
    if not prompt:
        return sdk_error("prompt is required")

    budget_tokens = max(1024, min(int(args.get("budget_tokens", 8000)), 32000))
    model = str(args.get("model", "claude-sonnet-4-5-20250929"))
    system = args.get("system")
    max_tokens = max(budget_tokens + 1024, int(args.get("max_tokens", 16000)))
    include_thinking = bool(args.get("include_thinking", True))

    try:
        import anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
        client = anthropic.Anthropic(api_key=api_key, base_url=base_url)

        create_kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "thinking": {"type": "enabled", "budget_tokens": budget_tokens},
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            create_kwargs["system"] = system

        response = client.messages.create(**create_kwargs)

        thinking_blocks: list[str] = []
        text_blocks: list[str] = []

        for block in response.content:
            if block.type == "thinking":
                thinking_blocks.append(block.thinking)
            elif block.type == "text":
                text_blocks.append(block.text)

        result: dict[str, Any] = {
            "answer": "\n".join(text_blocks),
            "model": model,
            "budget_tokens": budget_tokens,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }
        if include_thinking:
            result["thinking"] = "\n\n---\n\n".join(thinking_blocks)
            result["thinking_blocks"] = len(thinking_blocks)

        return sdk_result(result)

    except Exception as exc:
        return sdk_error(f"invoke_with_thinking failed: {exc}")


@tool(
    "thinking_stream",
    "Stream a thinking-enabled response, surfacing reasoning blocks as they arrive.",
    {
        "prompt": {"type": "string", "description": "The question or task"},
        "budget_tokens": {"type": "integer", "default": 8000},
        "model": {"type": "string", "default": "claude-sonnet-4-5-20250929"},
        "system": {"type": "string", "description": "Optional system prompt"},
    },
)
async def thinking_stream(args: dict[str, Any]) -> JsonDict:
    prompt = str(args.get("prompt", "")).strip()
    if not prompt:
        return sdk_error("prompt is required")

    budget_tokens = max(1024, min(int(args.get("budget_tokens", 8000)), 32000))
    model = str(args.get("model", "claude-sonnet-4-5-20250929"))
    system = args.get("system")
    max_tokens = budget_tokens + 4096

    try:
        import anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
        client = anthropic.Anthropic(api_key=api_key, base_url=base_url)

        stream_kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "thinking": {"type": "enabled", "budget_tokens": budget_tokens},
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            stream_kwargs["system"] = system

        thinking_parts: list[str] = []
        text_parts: list[str] = []

        with client.messages.stream(**stream_kwargs) as stream:
            for event in stream:
                pass  # consume — full content collected in final message
            final = stream.get_final_message()

        for block in final.content:
            if block.type == "thinking":
                thinking_parts.append(block.thinking)
            elif block.type == "text":
                text_parts.append(block.text)

        return sdk_result({
            "answer": "\n".join(text_parts),
            "thinking": "\n\n---\n\n".join(thinking_parts),
            "thinking_blocks": len(thinking_parts),
            "model": model,
            "budget_tokens": budget_tokens,
            "input_tokens": final.usage.input_tokens,
            "output_tokens": final.usage.output_tokens,
        })

    except Exception as exc:
        return sdk_error(f"thinking_stream failed: {exc}")


ALL_TOOLS = [invoke_with_thinking, thinking_stream]
