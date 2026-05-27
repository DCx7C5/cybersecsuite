"""Routing request-complexity primitives and classifier."""

from collections.abc import Mapping, Sequence
from enum import Enum

import msgspec

from .token_counter import TokenCounter

_TOOL_KEYWORDS = ("tool", "function call", "shell", "bash", "api call")
_VISION_KEYWORDS = ("image", "screenshot", "vision", "ocr", "pdf", "file upload")
_CODE_KEYWORDS = ("code", "python", "javascript", "function", "class", "exploit", "snippet")
_REASONING_KEYWORDS = ("compare", "plan", "analyze", "reason", "tradeoff", "evaluate")
_SECURITY_KEYWORDS = (
    "security",
    "exploit",
    "penetration",
    "xss",
    "sqli",
    "rce",
    "payload",
    "vulnerability",
    "cve",
    "attack",
)


class RequestComplexity(str, Enum):
    """Request complexity buckets for tier selection."""

    TRIVIAL = "TRIVIAL"
    SIMPLE = "SIMPLE"
    MODERATE = "MODERATE"
    COMPLEX = "COMPLEX"
    CRITICAL = "CRITICAL"


class TriageMetrics(msgspec.Struct, frozen=True, kw_only=True):
    """Routing triage summary used by tier and router selection."""

    input_length: int
    estimated_tokens: int
    complexity: RequestComplexity
    has_tool_use: bool
    requires_vision: bool
    has_code_generation: bool
    requires_reasoning: bool
    security_level: int


def _extract_text_blob(messages: object, system: object) -> str:
    parts: list[str] = []
    if isinstance(system, str) and system:
        parts.append(system)
    if isinstance(messages, str):
        parts.append(messages)
    elif isinstance(messages, Sequence):
        for item in messages:
            if isinstance(item, Mapping):
                content = item.get("content")
                if isinstance(content, str) and content:
                    parts.append(content)
            elif isinstance(item, str) and item:
                parts.append(item)
    return "\n".join(parts)


def _coerce_request_parts(request: object) -> tuple[object, str | None, object | None, str | None, str | None]:
    if isinstance(request, str):
        return request, None, None, None, None
    if isinstance(request, Mapping):
        return (
            request.get("messages", request.get("prompt", "")),
            request.get("system") if isinstance(request.get("system"), str) else None,
            request.get("tools"),
            request.get("model") if isinstance(request.get("model"), str) else None,
            request.get("provider_id") if isinstance(request.get("provider_id"), str) else None,
        )
    messages = getattr(request, "messages", "")
    system = getattr(request, "system", None)
    tools = getattr(request, "tools", None)
    model = getattr(request, "model", None)
    provider_id = getattr(request, "provider_id", None)
    return (
        messages,
        system if isinstance(system, str) else None,
        tools,
        model if isinstance(model, str) else None,
        provider_id if isinstance(provider_id, str) else None,
    )


def _fallback_token_estimate(text_blob: str) -> int:
    word_count = len([word for word in text_blob.split() if word])
    return max(1, word_count)


def _complexity_from_tokens(estimated_tokens: int) -> RequestComplexity:
    if estimated_tokens < 50:
        return RequestComplexity.TRIVIAL
    if estimated_tokens <= 200:
        return RequestComplexity.SIMPLE
    if estimated_tokens <= 1000:
        return RequestComplexity.MODERATE
    if estimated_tokens <= 4000:
        return RequestComplexity.COMPLEX
    return RequestComplexity.CRITICAL


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _security_level(text: str) -> int:
    hits = sum(1 for term in _SECURITY_KEYWORDS if term in text)
    return max(1, min(10, 1 + hits * 2))


def analyze_complexity(request: object, token_counter: TokenCounter | None = None) -> TriageMetrics:
    """Return one triage metrics object for routing."""
    messages, system, tools, model, provider_id = _coerce_request_parts(request)
    text_blob = _extract_text_blob(messages, system)
    lower_text = text_blob.lower()

    effective_counter = token_counter or TokenCounter()
    estimated = effective_counter.count(
        model=model or "unknown",
        messages=messages,
        system=system,
        tools=tools,
        provider_id=provider_id,
    )
    estimated_tokens = estimated if estimated is not None else _fallback_token_estimate(text_blob)

    tools_present = isinstance(tools, Sequence) and not isinstance(tools, str | bytes) and len(tools) > 0
    has_tool_use = tools_present or _contains_any(lower_text, _TOOL_KEYWORDS)
    requires_vision = _contains_any(lower_text, _VISION_KEYWORDS)
    has_code_generation = _contains_any(lower_text, _CODE_KEYWORDS)
    requires_reasoning = _contains_any(lower_text, _REASONING_KEYWORDS)

    return TriageMetrics(
        input_length=len(text_blob),
        estimated_tokens=estimated_tokens,
        complexity=_complexity_from_tokens(estimated_tokens),
        has_tool_use=has_tool_use,
        requires_vision=requires_vision,
        has_code_generation=has_code_generation,
        requires_reasoning=requires_reasoning,
        security_level=_security_level(lower_text),
    )
