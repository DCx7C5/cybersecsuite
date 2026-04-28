"""
Playwright-based executor for browser-automated LLM providers.

Uses the playwright-stealth-mcp infrastructure to interact with web-based
LLM interfaces that don't offer API access (or for session-based auth like
Claude web, ChatGPT web, etc.).

Requires: playwright, playwright-stealth
"""


import asyncio
import logging
import time
from typing import Any

from ai_proxy.executors.base import BaseExecutor, ExecutorResult
from src.registries.providers import ProviderConfig

logger = logging.getLogger("ai_proxy.executor.playwright")

# Lazy imports — playwright is optional
_playwright_available: bool | None = None


def _check_playwright() -> bool:
    global _playwright_available
    if _playwright_available is None:
        try:
            import playwright  # noqa: F401
            _playwright_available = True
        except ImportError:
            _playwright_available = False
            logger.warning(
                "Playwright not installed — browser providers unavailable. "
                "Install with: uv add playwright playwright-stealth"
            )
    return _playwright_available


class PlaywrightExecutor(BaseExecutor):
    """
    Executor that drives a browser to interact with web-based LLM UIs.

    Config via ProviderConfig:
      - base_url:          The chat UI URL (e.g. https://chat.openai.com)
      - browser_profile:   Path to persistent browser profile dir
      - browser_executable: Path to browser binary (Brave, Chrome, etc.)
      - headless:          Run headless (default True)
      - extra:             Dict with selectors and behavior config:
          - input_selector:   CSS selector for the text input
          - submit_selector:  CSS selector for the submit button
          - output_selector:  CSS selector for the response container
          - wait_selector:    CSS selector to wait for (response complete)
          - wait_timeout_ms:  Max wait time for response (default 120000)
          - pre_auth_url:     URL to navigate for auth before sending
    """

    def __init__(self, provider: ProviderConfig):
        super().__init__(provider)
        self._context = None
        self._page = None
        self._pw = None

    def build_url(self, model: str, endpoint: str = "chat/completions") -> str:
        return self.provider.base_url

    async def _ensure_browser(self):
        """Launch or reuse a persistent browser context."""
        if self._page is not None:
            return

        if not _check_playwright():
            raise RuntimeError("Playwright is not installed")

        from playwright.async_api import async_playwright

        self._pw = await async_playwright().__aenter__()

        launch_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled",
        ]

        profile_dir = self.provider.browser_profile
        executable = self.provider.browser_executable

        if profile_dir:
            self._context = await self._pw.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                executable_path=executable,
                headless=self.provider.headless,
                args=launch_args,
                viewport={"width": 1920, "height": 1080},
            )
            self._page = self._context.pages[0] if self._context.pages else await self._context.new_page()
        else:
            browser = await self._pw.chromium.launch(
                executable_path=executable,
                headless=self.provider.headless,
                args=launch_args,
            )
            self._context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
            )
            self._page = await self._context.new_page()

        # Apply stealth if available
        try:
            from playwright_stealth import Stealth
            stealth = Stealth()
            await stealth.apply(self._page)
        except ImportError:
            logger.debug("playwright-stealth not available, proceeding without stealth")

    async def execute(
        self,
        body: dict[str, Any],
        model: str,
        stream: bool = False,
        endpoint: str = "chat/completions",
    ) -> ExecutorResult:
        """Execute a chat completion via browser automation."""
        start = time.monotonic()

        try:
            await self._ensure_browser()
        except Exception as exc:
            return ExecutorResult(
                status_code=503,
                error=f"Browser launch failed: {exc}",
                provider_id=self.provider.id,
                model_id=model,
            )

        extra = self.provider.extra
        input_selector = extra.get("input_selector", 'textarea[data-id="root"]')
        submit_selector = extra.get("submit_selector", 'button[data-testid="send-button"]')
        output_selector = extra.get("output_selector", '[data-message-author-role="assistant"]')
        wait_timeout = extra.get("wait_timeout_ms", 120_000)

        # Extract user message from OpenAI format
        messages = body.get("messages", [])
        user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                user_msg = content if isinstance(content, str) else str(content)
                break

        if not user_msg:
            return ExecutorResult(
                status_code=400,
                error="No user message found in request",
                provider_id=self.provider.id,
                model_id=model,
            )

        try:
            page = self._page

            # Navigate if needed
            if page.url == "about:blank" or self.provider.base_url not in page.url:
                pre_auth = extra.get("pre_auth_url", self.provider.base_url)
                await page.goto(pre_auth, wait_until="domcontentloaded", timeout=30_000)
                await asyncio.sleep(2)  # Let page settle

            # Type message with human-like delay
            await page.wait_for_selector(input_selector, timeout=10_000)
            await page.click(input_selector)

            # Type character by character with slight delay for anti-bot
            for char in user_msg:
                await page.keyboard.type(char, delay=20 + (hash(char) % 30))

            # Count existing responses before submitting
            existing_responses = await page.query_selector_all(output_selector)
            existing_count = len(existing_responses)

            # Submit
            await page.click(submit_selector)

            # Wait for new response to appear
            await page.wait_for_function(
                f"""() => document.querySelectorAll('{output_selector}').length > {existing_count}""",
                timeout=wait_timeout,
            )

            # Wait a bit for streaming to complete
            await asyncio.sleep(2)

            # Check if still streaming (look for a typing indicator)
            for _ in range(60):  # Max 60 seconds additional wait
                is_streaming = await page.evaluate(
                    """() => {
                        const indicators = document.querySelectorAll('.typing-indicator, .streaming, [data-streaming="true"]');
                        return indicators.length > 0;
                    }"""
                )
                if not is_streaming:
                    break
                await asyncio.sleep(1)

            # Extract response text
            responses = await page.query_selector_all(output_selector)
            if len(responses) > existing_count:
                last_response = responses[-1]
                response_text = await last_response.inner_text()
            else:
                response_text = ""

            latency = (time.monotonic() - start) * 1000

            # Format as OpenAI response
            return ExecutorResult(
                status_code=200,
                body={
                    "id": f"browser-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": response_text.strip(),
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": len(user_msg.split()) * 2,  # rough estimate
                        "completion_tokens": len(response_text.split()) * 2,
                        "total_tokens": (len(user_msg.split()) + len(response_text.split())) * 2,
                    },
                },
                latency_ms=latency,
                provider_id=self.provider.id,
                model_id=model,
            )

        except Exception as exc:
            latency = (time.monotonic() - start) * 1000
            logger.exception("Browser execution failed for %s", self.provider.id)
            return ExecutorResult(
                status_code=502,
                error=f"Browser error: {exc}",
                latency_ms=latency,
                provider_id=self.provider.id,
                model_id=model,
            )

    async def close(self) -> None:
        """Close browser context."""
        try:
            if self._context:
                await self._context.close()
                self._context = None
                self._page = None
            if self._pw:
                await self._pw.__aexit__(None, None, None)
                self._pw = None
        except Exception:
            pass
        await super().close()

