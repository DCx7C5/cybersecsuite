from collections.abc import AsyncIterator, Awaitable
from inspect import isawaitable
from typing import Any, cast

from css.core.sdks.adapters.browser_relay import BrowserRelayAdapter
from css.core.sdks.adapters.deepseek import DeepSeekAdapter
from css.core.sdks.relay_router import RelayAttempt, RelayProviderPolicy
from css.core.sdks.registry import SDKRegistry
from css.core.types.base_client import BaseApiServiceClient
from css.core.types.base_messages import LLMResponse
from css.core.utils.token_counter import estimate_message_tokens
from css.core.models import get_model_registry

_BROWSER_RELAY_PROVIDER_IDS = {
    "browser-relay",
    "browser_relay",
    "browser-plugin",
    "browser_plugin",
}
_DEEPSEEK_PROVIDER_IDS = {
    "deepseek",
    "deepseek-ai",
    "deepseek_ai",
}
_RELAY_CONTROL_KEYS = {
    "relay_provider_order",
    "relay_model_overrides",
    "relay_sdk_init",
}
_BROWSER_ONLY_KEYS = {
    "browser_plugin_session_id",
    "session_id",
    "request_id",
    "request_ttl_seconds",
    "poll_interval_seconds",
    "poll_timeout_seconds",
    "cancel_event",
}


class CSSLLMClient:
    """Unified LLM client that routes to registered SDK adapters.

    Usage:
        client = CSSLLMClient()
        sdk = await client.get_sdk("openai", api_key="sk-...")
        async for chunk in await sdk.call_llm(model_id="gpt-4", messages=[...]):
            print(chunk.content)
    """

    def __init__(self) -> None:
        self._registry: SDKRegistry = SDKRegistry()
        self._model_registry = get_model_registry()
        self._register_builtin_sdks()

    @staticmethod
    def _normalize_provider_id(provider_id: str) -> str:
        normalized = provider_id.strip().lower()
        if normalized in _DEEPSEEK_PROVIDER_IDS:
            return "deepseek"
        return normalized

    def _register_builtin_sdks(self) -> None:
        if "deepseek" not in self._registry.list_registered():
            self._registry.register("deepseek", DeepSeekAdapter)

    @staticmethod
    def _relay_provider_call_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value
            for key, value in kwargs.items()
            if key not in _RELAY_CONTROL_KEYS and key not in _BROWSER_ONLY_KEYS
        }

    def _relay_model_overrides(self, kwargs: dict[str, Any]) -> dict[str, str]:
        model_overrides_obj = kwargs.get("relay_model_overrides")
        if not isinstance(model_overrides_obj, dict):
            return {}

        resolved: dict[str, str] = {}
        for provider_obj, model_obj in model_overrides_obj.items():
            if not isinstance(provider_obj, str) or not isinstance(model_obj, str):
                continue
            resolved[self._normalize_provider_id(provider_obj)] = model_obj
        return resolved

    def _relay_sdk_init_kwargs(self, kwargs: dict[str, Any], provider_id: str) -> dict[str, Any]:
        sdk_init_obj = kwargs.get("relay_sdk_init")
        if not isinstance(sdk_init_obj, dict):
            return {}

        provider_init = sdk_init_obj.get(provider_id)
        if isinstance(provider_init, dict):
            return dict(provider_init)

        # Allow alias lookup with normalized keys.
        for provider_obj, provider_kwargs in sdk_init_obj.items():
            if not isinstance(provider_obj, str) or not isinstance(provider_kwargs, dict):
                continue
            if self._normalize_provider_id(provider_obj) == provider_id:
                return dict(provider_kwargs)
        return {}

    @staticmethod
    def _relay_attempts_payload(attempts: list[RelayAttempt]) -> list[dict[str, str | None]]:
        return [
            {
                "provider_id": attempt.provider_id,
                "status": attempt.status,
                "reason": attempt.reason,
                "detail": attempt.detail,
            }
            for attempt in attempts
        ]

    def _relay_response_with_metadata(
        self,
        response: LLMResponse,
        *,
        selected_provider: str,
        attempts: list[RelayAttempt],
    ) -> LLMResponse:
        usage = dict(response.usage)
        usage["relay_selected_provider"] = selected_provider
        usage["relay_attempts"] = self._relay_attempts_payload(attempts)
        return LLMResponse(
            text=response.text,
            stop_reason=response.stop_reason,
            usage=usage,
        )

    async def _call_buffered_with_relay_priority(
        self,
        model_id: str,
        messages: list[Any],
        **kwargs: Any,
    ) -> LLMResponse:
        order_obj = kwargs.get("relay_provider_order")
        policy = RelayProviderPolicy.from_order(
            order_obj if isinstance(order_obj, (list, tuple)) else None
        )
        registered_providers = set(self._registry.list_registered())
        model_overrides = self._relay_model_overrides(kwargs)
        provider_call_kwargs = self._relay_provider_call_kwargs(kwargs)
        attempts: list[RelayAttempt] = []

        for provider_id in policy.ordered_providers():
            normalized_provider_id = self._normalize_provider_id(provider_id)

            if policy.is_web_relay_provider(normalized_provider_id):
                browser_model_id = model_overrides.get(normalized_provider_id, model_id)
                try:
                    web_relay_kwargs = dict(kwargs)
                    web_relay_kwargs["relay_provider_id"] = normalized_provider_id
                    response = await BrowserRelayAdapter().call_llm_buffered(
                        model_id=browser_model_id,
                        messages=messages,
                        **web_relay_kwargs,
                    )
                    attempts.append(
                        RelayAttempt(
                            provider_id=normalized_provider_id,
                            status="success",
                            reason="selected",
                        )
                    )
                    return self._relay_response_with_metadata(
                        response,
                        selected_provider=normalized_provider_id,
                        attempts=attempts,
                    )
                except Exception as exc:  # pragma: no cover - defensive fallback
                    attempts.append(
                        RelayAttempt(
                            provider_id=normalized_provider_id,
                            status="failed",
                            reason="call_error",
                            detail=str(exc),
                        )
                    )
                continue

            if normalized_provider_id not in registered_providers:
                attempts.append(
                    RelayAttempt(
                        provider_id=normalized_provider_id,
                        status="skipped",
                        reason="unavailable",
                    )
                )
                continue

            try:
                sdk_init_kwargs = self._relay_sdk_init_kwargs(kwargs, normalized_provider_id)
                sdk = await self._registry.get(normalized_provider_id, **sdk_init_kwargs)
                provider_model_id = model_overrides.get(normalized_provider_id, model_id)
                response = await sdk.call_llm_buffered(
                    model_id=provider_model_id,
                    messages=messages,
                    **provider_call_kwargs,
                )
                attempts.append(
                    RelayAttempt(
                        provider_id=normalized_provider_id,
                        status="success",
                        reason="selected",
                    )
                )
                return self._relay_response_with_metadata(
                    response,
                    selected_provider=normalized_provider_id,
                    attempts=attempts,
                )
            except Exception as exc:
                attempts.append(
                    RelayAttempt(
                        provider_id=normalized_provider_id,
                        status="failed",
                        reason="call_error",
                        detail=str(exc),
                    )
                )

        return LLMResponse(
            text="",
            stop_reason="relay_provider_exhausted",
            usage={
                "relay_selected_provider": "none",
                "relay_attempts": self._relay_attempts_payload(attempts),
            },
        )

    async def get_sdk(
        self,
        provider_id: str,
        **kwargs: Any,
    ) -> BaseApiServiceClient:
        normalized_provider_id = self._normalize_provider_id(provider_id)
        return await self._registry.get(normalized_provider_id, **kwargs)

    async def call(
        self,
        provider_id: str,
        model_id: str,
        messages: list[Any],
        **kwargs: Any,
    ) -> AsyncIterator[Any]:
        normalized_provider_id = self._normalize_provider_id(provider_id)
        if normalized_provider_id in _BROWSER_RELAY_PROVIDER_IDS:
            adapter = BrowserRelayAdapter()
            return await adapter.call_llm(
                model_id=model_id,
                messages=messages,
                **kwargs,
            )

        sdk = await self._registry.get(normalized_provider_id, **kwargs)
        stream_or_future = sdk.call_llm(
            model_id=model_id,
            messages=messages,
            **kwargs,
        )
        if isawaitable(stream_or_future):
            return await cast(Awaitable[AsyncIterator[Any]], stream_or_future)
        return cast(AsyncIterator[Any], stream_or_future)

    async def call_buffered(
        self,
        provider_id: str,
        model_id: str,
        messages: list[Any],
        **kwargs: Any,
    ) -> LLMResponse:
        normalized_provider_id = self._normalize_provider_id(provider_id)
        if normalized_provider_id in _BROWSER_RELAY_PROVIDER_IDS:
            return await self._call_buffered_with_relay_priority(
                model_id=model_id,
                messages=messages,
                **kwargs,
            )

        sdk = await self._registry.get(normalized_provider_id, **kwargs)
        return await sdk.call_llm_buffered(
            model_id=model_id,
            messages=messages,
            **kwargs,
        )

    async def estimate_tokens(
        self,
        model_id: str,
        messages: list[dict[str, Any]],
    ) -> int:
        """Estimate token count for messages using the model's tokenizer.

        Attempts to use the provider SDK's tokenizer if available.
        Falls back to heuristic estimation if not supported.

        Args:
            model_id: Model identifier (e.g., 'gpt-4', 'claude-opus')
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Estimated token count
        """
        # Try provider-specific token counting first
        try:
            # Check if model has a documented token count method
            # (e.g., via OpenAI's encoding or Anthropic's token counter)
            # For now, use heuristic fallback
            pass
        except Exception:
            pass

        # Fallback to heuristic token counting
        return estimate_message_tokens(messages)

    def clear_cache(self, provider_id: str | None = None) -> None:
        self._registry.clear_cache(provider_id)

    def list_registered(self) -> list[str]:
        return self._registry.list_registered()


UniversalLLMClient = CSSLLMClient
