from typing import Any

import pytest

from css.core.sdks import CSSLLMClient, SDKRegistry
from css.core.sdks.adapters.browser_relay import BrowserRelayAdapter
from css.core.sdks.adapters.deepseek import DeepSeekAdapter
from css.core.sdks.relay_router import RelayProviderPolicy
from css.core.messages.types import LLMResponse


def test_relay_provider_policy_is_deterministic() -> None:
    policy = RelayProviderPolicy.from_order(
        ["OpenAI", "deepseek", "openai", "  ", "web_relay"]
    )
    assert policy.ordered_providers() == ["openai", "deepseek", "web_relay"]


@pytest.mark.asyncio
async def test_browser_relay_priority_skips_unavailable_and_selects_deepseek(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _deepseek_success(
        self: DeepSeekAdapter,
        model_id: str,
        messages: list[Any],
        **kwargs: Any,
    ) -> LLMResponse:
        assert model_id == "deepseek-chat"
        assert messages
        assert kwargs == {}
        return LLMResponse(text="deepseek ok", stop_reason="stop", usage={})

    monkeypatch.setattr(DeepSeekAdapter, "call_llm_buffered", _deepseek_success)

    registry = SDKRegistry()
    registry.clear_cache("deepseek")
    registry.register("deepseek", DeepSeekAdapter)

    client = CSSLLMClient()
    response = await client.call_buffered(
        provider_id="browser-relay",
        model_id="deepseek-chat",
        messages=[{"role": "user", "content": "hello"}],
        relay_provider_order=["github", "codex", "deepseek", "web_relay"],
    )
    assert response.text == "deepseek ok"
    assert response.usage["relay_selected_provider"] == "deepseek"

    attempts = response.usage["relay_attempts"]
    assert attempts[0]["provider_id"] == "github"
    assert attempts[0]["status"] == "skipped"
    assert attempts[1]["provider_id"] == "codex"
    assert attempts[1]["status"] == "skipped"
    assert attempts[2]["provider_id"] == "deepseek"
    assert attempts[2]["status"] == "success"


@pytest.mark.asyncio
async def test_browser_relay_priority_fallthrough_to_web_relay(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _deepseek_fail(
        self: DeepSeekAdapter,
        model_id: str,
        messages: list[Any],
        **kwargs: Any,
    ) -> LLMResponse:
        raise RuntimeError("deepseek failed")

    async def _web_relay_success(
        self: BrowserRelayAdapter,
        model_id: str,
        messages: list[Any],
        **kwargs: Any,
    ) -> LLMResponse:
        assert kwargs["browser_plugin_session_id"] == "plugin_session_test"
        return LLMResponse(text="browser fallback", stop_reason="stop", usage={})

    monkeypatch.setattr(DeepSeekAdapter, "call_llm_buffered", _deepseek_fail)
    monkeypatch.setattr(BrowserRelayAdapter, "call_llm_buffered", _web_relay_success)

    registry = SDKRegistry()
    registry.clear_cache("deepseek")
    registry.register("deepseek", DeepSeekAdapter)

    client = CSSLLMClient()
    response = await client.call_buffered(
        provider_id="browser-relay",
        model_id="deepseek-chat",
        messages=[{"role": "user", "content": "hello"}],
        browser_plugin_session_id="plugin_session_test",
        relay_provider_order=["deepseek", "web_relay"],
    )
    assert response.text == "browser fallback"
    assert response.usage["relay_selected_provider"] == "web_relay"

    attempts = response.usage["relay_attempts"]
    assert attempts[0]["provider_id"] == "deepseek"
    assert attempts[0]["status"] == "failed"
    assert attempts[1]["provider_id"] == "web_relay"
    assert attempts[1]["status"] == "success"
