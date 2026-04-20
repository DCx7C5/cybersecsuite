"""
API Format Translators — convert between OpenAI, Anthropic, and Gemini formats.

Mirrors OmniRoute's open-sse/translator/: bidirectional request/response
translation so any client format can talk to any provider format.
"""
from __future__ import annotations

from typing import Any

from ai_proxy.providers.registry import ApiFormat


# ── OpenAI → Anthropic ───────────────────────────────────────────────────────

def openai_to_anthropic_request(body: dict[str, Any]) -> dict[str, Any]:
    """Translate OpenAI chat completion request to Anthropic messages API."""
    messages = body.get("messages", [])
    system_parts: list[str] = []
    converted: list[dict[str, Any]] = []

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "system":
            system_parts.append(content if isinstance(content, str) else str(content))
            continue

        anthropic_role = "assistant" if role == "assistant" else "user"

        if isinstance(content, list):
            # Multi-modal content blocks
            blocks: list[dict[str, Any]] = []
            for part in content:
                if part.get("type") == "text":
                    blocks.append({"type": "text", "text": part["text"]})
                elif part.get("type") == "image_url":
                    url = part["image_url"]["url"]
                    if url.startswith("data:"):
                        media_type, _, b64 = url.partition(";base64,")
                        media_type = media_type.replace("data:", "")
                        blocks.append({
                            "type": "image",
                            "source": {"type": "base64", "media_type": media_type, "data": b64},
                        })
                    else:
                        blocks.append({
                            "type": "image",
                            "source": {"type": "url", "url": url},
                        })
            converted.append({"role": anthropic_role, "content": blocks})
        else:
            converted.append({"role": anthropic_role, "content": content})

    result: dict[str, Any] = {
        "model": body.get("model", ""),
        "messages": converted,
        "max_tokens": body.get("max_tokens") or body.get("max_completion_tokens") or 4096,
    }

    if system_parts:
        result["system"] = "\n\n".join(system_parts)

    if body.get("temperature") is not None:
        result["temperature"] = body["temperature"]
    if body.get("top_p") is not None:
        result["top_p"] = body["top_p"]
    if body.get("stream"):
        result["stream"] = True

    # Tool support
    tools = body.get("tools")
    if tools:
        result["tools"] = [
            {
                "name": t["function"]["name"],
                "description": t["function"].get("description", ""),
                "input_schema": t["function"].get("parameters", {}),
            }
            for t in tools
            if t.get("type") == "function"
        ]

    return result


def anthropic_to_openai_response(resp: dict[str, Any]) -> dict[str, Any]:
    """Translate Anthropic messages response to OpenAI chat completion format."""
    content_blocks = resp.get("content", [])
    text_parts = [b["text"] for b in content_blocks if b.get("type") == "text"]
    tool_calls = []

    for i, b in enumerate(content_blocks):
        if b.get("type") == "tool_use":
            tool_calls.append({
                "id": b.get("id", f"call_{i}"),
                "type": "function",
                "function": {
                    "name": b["name"],
                    "arguments": _json_dumps(b.get("input", {})),
                },
            })

    finish_reason_map = {
        "end_turn": "stop",
        "max_tokens": "length",
        "tool_use": "tool_calls",
        "stop_sequence": "stop",
    }

    message: dict[str, Any] = {
        "role": "assistant",
        "content": "\n".join(text_parts) if text_parts else None,
    }
    if tool_calls:
        message["tool_calls"] = tool_calls

    usage = resp.get("usage", {})

    return {
        "id": resp.get("id", ""),
        "object": "chat.completion",
        "created": 0,
        "model": resp.get("model", ""),
        "choices": [
            {
                "index": 0,
                "message": message,
                "finish_reason": finish_reason_map.get(resp.get("stop_reason", ""), "stop"),
            }
        ],
        "usage": {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
        },
    }


# ── OpenAI → Gemini ──────────────────────────────────────────────────────────

def openai_to_gemini_request(body: dict[str, Any]) -> dict[str, Any]:
    """Translate OpenAI chat completion request to Gemini generateContent format."""
    messages = body.get("messages", [])
    contents: list[dict[str, Any]] = []
    system_instruction: str | None = None

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "system":
            system_instruction = content if isinstance(content, str) else str(content)
            continue

        gemini_role = "model" if role == "assistant" else "user"

        if isinstance(content, list):
            parts = []
            for part in content:
                if part.get("type") == "text":
                    parts.append({"text": part["text"]})
                elif part.get("type") == "image_url":
                    url = part["image_url"]["url"]
                    if url.startswith("data:"):
                        media_type, _, b64 = url.partition(";base64,")
                        media_type = media_type.replace("data:", "")
                        parts.append({"inline_data": {"mime_type": media_type, "data": b64}})
            contents.append({"role": gemini_role, "parts": parts})
        else:
            contents.append({"role": gemini_role, "parts": [{"text": content}]})

    result: dict[str, Any] = {"contents": contents}

    if system_instruction:
        result["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    gen_config: dict[str, Any] = {}
    if body.get("temperature") is not None:
        gen_config["temperature"] = body["temperature"]
    if body.get("top_p") is not None:
        gen_config["topP"] = body["top_p"]
    if body.get("max_tokens"):
        gen_config["maxOutputTokens"] = body["max_tokens"]
    if gen_config:
        result["generationConfig"] = gen_config

    return result


def gemini_to_openai_response(resp: dict[str, Any]) -> dict[str, Any]:
    """Translate Gemini generateContent response to OpenAI chat completion format."""
    candidates = resp.get("candidates", [{}])
    candidate = candidates[0] if candidates else {}
    parts = candidate.get("content", {}).get("parts", [])
    text = "\n".join(p.get("text", "") for p in parts if "text" in p)

    finish_map = {
        "STOP": "stop",
        "MAX_TOKENS": "length",
        "SAFETY": "content_filter",
    }

    usage_meta = resp.get("usageMetadata", {})

    return {
        "id": "",
        "object": "chat.completion",
        "created": 0,
        "model": resp.get("modelVersion", ""),
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": finish_map.get(candidate.get("finishReason", ""), "stop"),
            }
        ],
        "usage": {
            "prompt_tokens": usage_meta.get("promptTokenCount", 0),
            "completion_tokens": usage_meta.get("candidatesTokenCount", 0),
            "total_tokens": usage_meta.get("totalTokenCount", 0),
        },
    }


# ── Dispatcher ───────────────────────────────────────────────────────────────

def translate_request(
    body: dict[str, Any],
    source_format: ApiFormat,
    target_format: ApiFormat,
) -> dict[str, Any]:
    """Translate request body between API formats."""
    if source_format == target_format:
        return body

    # Custom format: pass-through (client sends raw format, target handles it)
    if target_format == ApiFormat.CUSTOM:
        return body

    key = (source_format, target_format)
    translator = _REQUEST_TRANSLATORS.get(key)
    if translator is None:
        raise ValueError(f"No translator for {source_format.value} → {target_format.value}")
    return translator(body)


def translate_response(
    resp: dict[str, Any],
    source_format: ApiFormat,
    target_format: ApiFormat,
) -> dict[str, Any]:
    """Translate response body between API formats."""
    if source_format == target_format:
        return resp

    # Custom format: pass-through (provider sends raw format, client handles it)
    if source_format == ApiFormat.CUSTOM:
        return resp

    key = (source_format, target_format)
    translator = _RESPONSE_TRANSLATORS.get(key)
    if translator is None:
        raise ValueError(f"No response translator for {source_format.value} → {target_format.value}")
    return translator(resp)


_REQUEST_TRANSLATORS = {
    (ApiFormat.OPENAI, ApiFormat.ANTHROPIC): openai_to_anthropic_request,
    (ApiFormat.OPENAI, ApiFormat.GEMINI): openai_to_gemini_request,
}

_RESPONSE_TRANSLATORS = {
    (ApiFormat.ANTHROPIC, ApiFormat.OPENAI): anthropic_to_openai_response,
    (ApiFormat.GEMINI, ApiFormat.OPENAI): gemini_to_openai_response,
}


def _json_dumps(obj: Any) -> str:
    import json
    return json.dumps(obj, separators=(",", ":"))

