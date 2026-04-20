"""
SDK Tool Runner — agentic loop using Anthropic beta.messages.tool_runner.

Provides a clean wrapper for running multi-turn tool-calling loops using the
official SDK's tool_runner. Handles tool dispatch automatically without a
manual inject-result loop.

Usage:
    runner = SdkToolRunner(provider_id="anthropic")
    result = await runner.run(
        model="claude-3-5-sonnet-20241022",
        prompt="Analyze this IOC: 192.168.1.1",
        tools=[my_tool_fn],
    )
    print(result.final_text)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

import anthropic

from ai_proxy.providers.registry import get_provider

logger = logging.getLogger("ai_proxy.tool_runner")


@dataclass
class ToolRunResult:
    """Result from a tool_runner loop."""
    final_text: str | None
    stop_reason: str
    tool_calls: int
    usage_input: int
    usage_output: int
    request_id: str | None = None


class SdkToolRunner:
    """
    Agentic loop using anthropic.beta.messages.tool_runner.

    Compared to a manual inject-result loop:
    - No boilerplate message-append code
    - SDK handles stop_reason checks and re-injection automatically
    - max_iterations guard built in
    """

    def __init__(self, provider_id: str = "anthropic") -> None:
        self._provider_id = provider_id
        self._sdk: anthropic.AsyncAnthropic | None = None

    def _get_sdk(self) -> anthropic.AsyncAnthropic | None:
        if self._sdk is not None:
            return self._sdk
        provider = get_provider(self._provider_id)
        if not provider:
            return None
        api_key = provider.get_api_key()
        if not api_key:
            return None
        self._sdk = anthropic.AsyncAnthropic(
            api_key=api_key,
            base_url=provider.base_url,
            max_retries=provider.max_retries,
        )
        return self._sdk

    async def run(
        self,
        model: str,
        prompt: str,
        tools: list[Callable[..., Any]],
        system: str | None = None,
        max_tokens: int = 4096,
        max_iterations: int = 10,
    ) -> ToolRunResult:
        """
        Run an agentic loop with tool_runner.

        The tools list accepts plain Python callables — the SDK introspects
        their signatures and docstrings to build ToolParam descriptions.

        Returns a ToolRunResult with the final text and usage stats.
        """
        sdk = self._get_sdk()
        if sdk is None:
            raise RuntimeError(f"Provider {self._provider_id!r} not configured or missing API key")

        messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "tools": tools,
            "messages": messages,
            "max_iterations": max_iterations,
        }
        if system:
            kwargs["system"] = system

        tool_call_count = 0
        final_text: str | None = None
        stop_reason = "end_turn"
        usage_input = 0
        usage_output = 0
        request_id: str | None = None

        try:
            async with sdk.beta.messages.tool_runner(**kwargs) as runner:
                # Stream events to track tool calls and collect final message
                async for _event in runner:
                    pass

            final_msg = runner.get_final_message()
            stop_reason = final_msg.stop_reason or "end_turn"
            request_id = getattr(final_msg, "_request_id", None)

            usage_input = getattr(final_msg.usage, "input_tokens", 0)
            usage_output = getattr(final_msg.usage, "output_tokens", 0)

            # Count tool_use blocks across all content
            for block in final_msg.content:
                if getattr(block, "type", None) == "tool_use":
                    tool_call_count += 1

            # Extract text from final message
            texts = [b.text for b in final_msg.content if getattr(b, "type", None) == "text"]
            final_text = "\n".join(texts) or None

        except anthropic.APIError as exc:
            logger.warning("tool_runner failed: %s", exc)
            raise

        return ToolRunResult(
            final_text=final_text,
            stop_reason=stop_reason,
            tool_calls=tool_call_count,
            usage_input=usage_input,
            usage_output=usage_output,
            request_id=request_id,
        )

    async def close(self) -> None:
        if self._sdk is not None:
            await self._sdk.close()
            self._sdk = None
