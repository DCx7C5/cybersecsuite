"""
API Format Translators — convert between OpenAI, Anthropic, and Gemini formats.

Bidirectional request/response
translation so any client format can talk to any provider format.
"""


import json
from typing import Any

from ai_proxy.providers.registry import ApiFormat


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"))


def _flatten_content_blocks(value: Any) -> str:
    """Normalize mixed string/content-block values to plain text."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: list[str] = []
        for block in value:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "\n".join(part for part in parts if part)
    return "" if value is None else str(value)


def _normalize_object_schema(schema: Any) -> dict[str, Any]:
    normalized = schema if isinstance(schema, dict) else {"type": "object", "properties": {}}
    if normalized.get("type") == "object" and "properties" not in normalized:
        normalized = {**normalized, "properties": {}}
    return normalized


def _openai_content_to_anthropic_blocks(content: Any) -> list[dict[str, Any]]:
    if isinstance(content, str):
        return [{"type": "text", "text": content}] if content else []
    if not isinstance(content, list):
        return [{"type": "text", "text": _flatten_content_blocks(content)}] if content else []

    blocks: list[dict[str, Any]] = []
    for part in content:
        if not isinstance(part, dict):
            continue
        if part.get("type") == "text":
            text = part.get("text")
            if text:
                blocks.append({"type": "text", "text": text})
        elif part.get("type") == "image_url":
            image_url = part.get("image_url") or {}
            url = image_url.get("url")
            if not isinstance(url, str) or not url:
                continue
            if url.startswith("data:"):
                media_type, _, b64 = url.partition(";base64,")
                blocks.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type.replace("data:", ""),
                        "data": b64,
                    },
                })
            else:
                blocks.append({"type": "image", "source": {"type": "url", "url": url}})
    return blocks


def _openai_content_to_gemini_parts(content: Any) -> list[dict[str, Any]]:
    if isinstance(content, str):
        return [{"text": content}] if content else []
    if not isinstance(content, list):
        text = _flatten_content_blocks(content)
        return [{"text": text}] if text else []

    parts: list[dict[str, Any]] = []
    for part in content:
        if not isinstance(part, dict):
            continue
        if part.get("type") == "text":
            text = part.get("text")
            if text:
                parts.append({"text": text})
        elif part.get("type") == "image_url":
            image_url = part.get("image_url") or {}
            url = image_url.get("url")
            if not isinstance(url, str) or not url:
                continue
            if url.startswith("data:"):
                media_type, _, b64 = url.partition(";base64,")
                parts.append({
                    "inlineData": {
                        "mimeType": media_type.replace("data:", ""),
                        "data": b64,
                    }
                })
    return parts


def _anthropic_tool_choice(tool_choice: Any) -> dict[str, Any] | None:
    if isinstance(tool_choice, str):
        if tool_choice == "required":
            return {"type": "any"}
        if tool_choice in {"auto", "none"}:
            return {"type": "auto"}
        return None
    if isinstance(tool_choice, dict):
        choice_type = tool_choice.get("type")
        if choice_type == "function":
            function_data = tool_choice.get("function") or {}
            name = function_data.get("name")
            if name:
                return {"type": "tool", "name": name}
        if choice_type in {"auto", "none"}:
            return {"type": "auto"}
    return None


def _gemini_function_declarations(tools: Any) -> list[dict[str, Any]]:
    declarations: list[dict[str, Any]] = []
    if not isinstance(tools, list):
        return declarations
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        if tool.get("type") != "function":
            continue
        function_data = tool.get("function") or {}
        name = function_data.get("name")
        if not name:
            continue
        declarations.append({
            "name": name,
            "description": function_data.get("description", ""),
            "parameters": _normalize_object_schema(function_data.get("parameters")),
        })
    return declarations


# ── OpenAI → Anthropic ───────────────────────────────────────────────────────

def openai_to_anthropic_request(body: dict[str, Any]) -> dict[str, Any]:
    """Translate OpenAI chat completion request to Anthropic messages API."""
    messages = body.get("messages", [])
    system_parts: list[str] = []
    converted: list[dict[str, Any]] = []

    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "system":
            system_text = _flatten_content_blocks(content)
            if system_text:
                system_parts.append(system_text)
            continue

        if role == "tool":
            tool_use_id = msg.get("tool_call_id")
            if tool_use_id:
                converted.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": _flatten_content_blocks(content),
                    }],
                })
            continue

        anthropic_role = "assistant" if role == "assistant" else "user"
        blocks = _openai_content_to_anthropic_blocks(content)

        if role == "assistant":
            for tool_call in msg.get("tool_calls", []):
                if not isinstance(tool_call, dict) or tool_call.get("type") != "function":
                    continue
                function_data = tool_call.get("function") or {}
                arguments = function_data.get("arguments", "{}")
                try:
                    parsed_arguments = json.loads(arguments) if isinstance(arguments, str) else arguments
                except json.JSONDecodeError:
                    parsed_arguments = {}
                blocks.append({
                    "type": "tool_use",
                    "id": tool_call.get("id", ""),
                    "name": function_data.get("name", ""),
                    "input": parsed_arguments if isinstance(parsed_arguments, dict) else {},
                })

        if blocks:
            converted.append({"role": anthropic_role, "content": blocks})

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
    if body.get("stop") is not None:
        result["stop_sequences"] = body["stop"] if isinstance(body["stop"], list) else [body["stop"]]
    if body.get("stream"):
        result["stream"] = True

    tools = body.get("tools")
    if isinstance(tools, list):
        result["tools"] = [
            {
                "name": function_data["name"],
                "description": function_data.get("description", ""),
                "input_schema": _normalize_object_schema(function_data.get("parameters")),
            }
            for tool in tools
            if isinstance(tool, dict)
            and tool.get("type") == "function"
            and isinstance((function_data := tool.get("function") or {}), dict)
            and function_data.get("name")
        ]

    tool_choice = _anthropic_tool_choice(body.get("tool_choice"))
    if tool_choice:
        result["tool_choice"] = tool_choice

    response_format = body.get("response_format")
    if isinstance(response_format, dict):
        if response_format.get("type") == "json_schema" and isinstance(response_format.get("json_schema"), dict):
            schema = response_format["json_schema"].get("schema") or response_format["json_schema"]
            system_parts.append(
                "Respond with valid JSON that strictly follows this schema:\n"
                f"{json.dumps(schema, indent=2)}"
            )
        elif response_format.get("type") == "json_object":
            system_parts.append("Respond with valid JSON only.")
        if system_parts:
            result["system"] = "\n\n".join(system_parts)

    return result


def anthropic_to_openai_response(resp: dict[str, Any]) -> dict[str, Any]:
    """Translate Anthropic messages response to OpenAI chat completion format."""
    content_blocks = resp.get("content", [])
    text_parts = [block["text"] for block in content_blocks if isinstance(block, dict) and block.get("type") == "text"]
    tool_calls = []

    for i, block in enumerate(content_blocks):
        if isinstance(block, dict) and block.get("type") == "tool_use":
            tool_calls.append({
                "id": block.get("id", f"call_{i}"),
                "type": "function",
                "function": {
                    "name": block.get("name", ""),
                    "arguments": _json_dumps(block.get("input", {})),
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
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)

    return {
        "id": resp.get("id", ""),
        "object": "chat.completion",
        "created": 0,
        "model": resp.get("model", ""),
        "choices": [{
            "index": 0,
            "message": message,
            "finish_reason": finish_reason_map.get(resp.get("stop_reason", ""), "stop"),
        }],
        "usage": {
            "prompt_tokens": input_tokens,
            "completion_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        },
    }


# ── OpenAI → Gemini ──────────────────────────────────────────────────────────

def openai_to_gemini_request(body: dict[str, Any]) -> dict[str, Any]:
    """Translate OpenAI chat completion request to Gemini generateContent format."""
    messages = body.get("messages", [])
    contents: list[dict[str, Any]] = []
    system_parts: list[str] = []
    tool_call_names: dict[str, str] = {}

    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "system":
            system_text = _flatten_content_blocks(content)
            if system_text:
                system_parts.append(system_text)
            continue

        if role == "tool":
            tool_call_id = msg.get("tool_call_id")
            if tool_call_id:
                contents.append({
                    "role": "user",
                    "parts": [{
                        "functionResponse": {
                            "id": tool_call_id,
                            "name": tool_call_names.get(tool_call_id, tool_call_id),
                            "response": {"result": _flatten_content_blocks(content)},
                        }
                    }],
                })
            continue

        gemini_role = "model" if role == "assistant" else "user"
        parts = _openai_content_to_gemini_parts(content)

        if role == "assistant":
            for tool_call in msg.get("tool_calls", []):
                if not isinstance(tool_call, dict) or tool_call.get("type") != "function":
                    continue
                function_data = tool_call.get("function") or {}
                arguments = function_data.get("arguments", "{}")
                try:
                    parsed_arguments = json.loads(arguments) if isinstance(arguments, str) else arguments
                except json.JSONDecodeError:
                    parsed_arguments = {}
                tool_call_id = tool_call.get("id", "")
                tool_name = function_data.get("name", "")
                if tool_call_id and tool_name:
                    tool_call_names[tool_call_id] = tool_name
                parts.append({
                    "functionCall": {
                        "id": tool_call_id,
                        "name": tool_name,
                        "args": parsed_arguments if isinstance(parsed_arguments, dict) else {},
                    }
                })

        if parts:
            contents.append({"role": gemini_role, "parts": parts})

    result: dict[str, Any] = {"contents": contents}

    if system_parts:
        result["systemInstruction"] = {"role": "user", "parts": [{"text": "\n\n".join(system_parts)}]}

    gen_config: dict[str, Any] = {}
    if body.get("temperature") is not None:
        gen_config["temperature"] = body["temperature"]
    if body.get("top_p") is not None:
        gen_config["topP"] = body["top_p"]
    if body.get("top_k") is not None:
        gen_config["topK"] = body["top_k"]
    if body.get("stop") is not None:
        gen_config["stopSequences"] = body["stop"] if isinstance(body["stop"], list) else [body["stop"]]
    if body.get("max_tokens") or body.get("max_completion_tokens"):
        gen_config["maxOutputTokens"] = body.get("max_tokens") or body.get("max_completion_tokens")

    response_format = body.get("response_format")
    if isinstance(response_format, dict):
        response_type = response_format.get("type")
        if response_type == "json_object":
            gen_config["responseMimeType"] = "application/json"
        elif response_type == "json_schema" and isinstance(response_format.get("json_schema"), dict):
            gen_config["responseMimeType"] = "application/json"
            schema = response_format["json_schema"].get("schema") or response_format["json_schema"]
            if isinstance(schema, dict):
                gen_config["responseSchema"] = schema
        elif response_type == "text":
            gen_config["responseMimeType"] = "text/plain"

    if gen_config:
        result["generationConfig"] = gen_config

    declarations = _gemini_function_declarations(body.get("tools"))
    if declarations:
        result["tools"] = [{"functionDeclarations": declarations}]

    return result


def gemini_to_openai_response(resp: dict[str, Any]) -> dict[str, Any]:
    """Translate Gemini generateContent response to OpenAI chat completion format."""
    candidates = resp.get("candidates", [{}])
    candidate = candidates[0] if candidates else {}
    parts = candidate.get("content", {}).get("parts", [])

    text_parts: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    for i, part in enumerate(parts):
        if not isinstance(part, dict):
            continue
        if "text" in part and part.get("text"):
            text_parts.append(part["text"])
        function_call = part.get("functionCall")
        if isinstance(function_call, dict):
            tool_calls.append({
                "id": function_call.get("id", f"call_{i}"),
                "type": "function",
                "function": {
                    "name": function_call.get("name", ""),
                    "arguments": _json_dumps(function_call.get("args", {})),
                },
            })

    finish_map = {
        "STOP": "stop",
        "MAX_TOKENS": "length",
        "SAFETY": "content_filter",
    }

    message: dict[str, Any] = {
        "role": "assistant",
        "content": "\n".join(text_parts) if text_parts else None,
    }
    if tool_calls:
        message["tool_calls"] = tool_calls

    usage_meta = resp.get("usageMetadata", {})

    return {
        "id": "",
        "object": "chat.completion",
        "created": 0,
        "model": resp.get("modelVersion", ""),
        "choices": [{
            "index": 0,
            "message": message,
            "finish_reason": finish_map.get(candidate.get("finishReason", ""), "stop"),
        }],
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

    if source_format == ApiFormat.CUSTOM:
        return resp

    key = (source_format, target_format)
    translator = _RESPONSE_TRANSLATORS.get(key)
    if translator is None:
        raise ValueError(f"No response translator for {source_format.value} → {target_format.value}")
    return translator(resp)


_ANTHROPIC_FAMILY = (
    ApiFormat.ANTHROPIC,
    ApiFormat.BEDROCK,
    ApiFormat.VERTEX,
    ApiFormat.FOUNDRY,
)

_REQUEST_TRANSLATORS = {
    (ApiFormat.OPENAI, ApiFormat.ANTHROPIC): openai_to_anthropic_request,
    (ApiFormat.OPENAI, ApiFormat.BEDROCK): openai_to_anthropic_request,
    (ApiFormat.OPENAI, ApiFormat.VERTEX): openai_to_anthropic_request,
    (ApiFormat.OPENAI, ApiFormat.FOUNDRY): openai_to_anthropic_request,
    (ApiFormat.OPENAI, ApiFormat.GEMINI): openai_to_gemini_request,
}

_RESPONSE_TRANSLATORS = {
    (ApiFormat.ANTHROPIC, ApiFormat.OPENAI): anthropic_to_openai_response,
    (ApiFormat.BEDROCK, ApiFormat.OPENAI): anthropic_to_openai_response,
    (ApiFormat.VERTEX, ApiFormat.OPENAI): anthropic_to_openai_response,
    (ApiFormat.FOUNDRY, ApiFormat.OPENAI): anthropic_to_openai_response,
    (ApiFormat.GEMINI, ApiFormat.OPENAI): gemini_to_openai_response,
}
