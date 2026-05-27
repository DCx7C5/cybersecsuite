"""Best-effort token counting for routing decisions."""

import importlib
import importlib.util
import json
from collections.abc import Mapping, Sequence


class TokenCounter:
    """Estimate or resolve token counts across providers."""

    def __init__(self, anthropic_client: object | None = None) -> None:
        self._anthropic_client = anthropic_client

    def _estimate_with_tiktoken(self, payload_text: str) -> int | None:
        spec = importlib.util.find_spec("tiktoken")
        if spec is None:
            return None
        tiktoken_module = importlib.import_module("tiktoken")
        encoder = tiktoken_module.get_encoding("cl100k_base")
        encoded = encoder.encode(payload_text)
        return len(encoded)

    @staticmethod
    def _extract_anthropic_count(result: object) -> int | None:
        if isinstance(result, int):
            return result
        if isinstance(result, Mapping):
            raw = result.get("input_tokens") or result.get("total_tokens")
            if isinstance(raw, int):
                return raw
            return None
        input_tokens = getattr(result, "input_tokens", None)
        if isinstance(input_tokens, int):
            return input_tokens
        total_tokens = getattr(result, "total_tokens", None)
        if isinstance(total_tokens, int):
            return total_tokens
        return None

    def _count_with_anthropic(
        self,
        model: str,
        messages: list[dict[str, object]],
        system: str | None,
        tools: object | None,
    ) -> int | None:
        if self._anthropic_client is None:
            return None
        messages_api = getattr(self._anthropic_client, "messages", None)
        if messages_api is None:
            return None
        count_tokens = getattr(messages_api, "count_tokens", None)
        if not callable(count_tokens):
            return None
        result = count_tokens(
            model=model,
            messages=messages,
            system=system,
            tools=tools,
        )
        return self._extract_anthropic_count(result)

    @staticmethod
    def _normalize_messages(messages: object) -> list[dict[str, object]]:
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        if isinstance(messages, Sequence):
            normalized: list[dict[str, object]] = []
            for item in messages:
                if isinstance(item, Mapping):
                    normalized.append(dict(item))
                elif isinstance(item, str):
                    normalized.append({"role": "user", "content": item})
            return normalized
        return []

    def count(
        self,
        model: str,
        messages: object,
        system: str | None = None,
        tools: object | None = None,
        provider_id: str | None = None,
    ) -> int | None:
        """Return token count or None when counting is unavailable."""
        try:
            normalized_messages = self._normalize_messages(messages)
            payload_text = json.dumps(
                {
                    "model": model,
                    "system": system,
                    "messages": normalized_messages,
                    "tools": tools,
                },
                sort_keys=True,
                default=str,
            )
        except (TypeError, ValueError):
            return None

        if provider_id is not None and provider_id.lower().startswith("anthropic"):
            anthropic_count = self._count_with_anthropic(
                model=model,
                messages=normalized_messages,
                system=system,
                tools=tools,
            )
            if anthropic_count is not None:
                return anthropic_count

        try:
            return self._estimate_with_tiktoken(payload_text)
        except (AttributeError, LookupError, TypeError, ValueError):
            return None
