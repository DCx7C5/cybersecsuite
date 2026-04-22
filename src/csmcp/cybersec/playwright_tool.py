"""Playwright browser automation tools for cybersec MCP server (T029).

Provides headless browser automation for forensic web-LLM interaction:
    playwright_navigate      — navigate to a URL
    playwright_inject_prompt — open a web LLM and inject a prompt
    playwright_screenshot    — capture a screenshot (base64 PNG)
    playwright_get_text      — extract visible text / element text

All tools degrade gracefully if playwright is not installed or the browser
context fails to start — they return sdk_error rather than raising.

Known web-LLM selectors (auto-detected by target URL when selector omitted):
    claude.ai   → div[contenteditable="true"]
    chat.openai.com → textarea#prompt-textarea
    grok.com / x.com/i/grok → textarea[data-testid]
    gemini.google.com → textarea, rich-textarea

Referenz: plan.md T029 — Phase 3: Browser Plugin
"""
from __future__ import annotations

import asyncio
import base64
import logging
from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import sdk_result, sdk_error

logger = logging.getLogger("csmcp.cybersec.playwright_tool")

# ---------------------------------------------------------------------------
# Known web-LLM prompt selectors keyed by hostname fragment
# ---------------------------------------------------------------------------
_KNOWN_SELECTORS: dict[str, str] = {
    "claude.ai":          'div[contenteditable="true"]',
    "chat.openai.com":    "textarea#prompt-textarea",
    "chatgpt.com":        "textarea#prompt-textarea",
    "grok.com":           'textarea[data-testid="tweetTextarea_0"]',
    "x.com":              'textarea[data-testid="tweetTextarea_0"]',
    "gemini.google.com":  "rich-textarea, textarea",
    "copilot.microsoft.com": 'textarea[name="q"]',
}


def _selector_for(url: str) -> str | None:
    """Return best-guess selector from known LLMs or None."""
    for fragment, sel in _KNOWN_SELECTORS.items():
        if fragment in url:
            return sel
    return None


# ---------------------------------------------------------------------------
# Lazy browser singleton
# ---------------------------------------------------------------------------
_browser_context = None
_page = None
_browser_lock = asyncio.Lock()


async def _ensure_page():
    """Lazily start a persistent stealth browser context. Raises on failure."""
    global _browser_context, _page
    async with _browser_lock:
        if _page is not None:
            try:
                await _page.evaluate("1")  # test if page is still alive
                return _page
            except Exception:
                _page = None
                _browser_context = None

        from playwright.async_api import async_playwright
        try:
            from playwright_stealth import Stealth
            _stealth = Stealth()
        except ImportError:
            _stealth = None

        pw = await async_playwright().start()
        _browser_context = await pw.chromium.launch_persistent_context(
            user_data_dir="/tmp/.cybersec_playwright_profile",
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--mute-audio",
            ],
        )
        _page = (
            _browser_context.pages[0]
            if _browser_context.pages
            else await _browser_context.new_page()
        )
        if _stealth:
            await _stealth.apply_stealth_async(_page)
        return _page


# ---------------------------------------------------------------------------
# Tool: playwright_navigate
# ---------------------------------------------------------------------------
@tool(
    "playwright_navigate",
    "Navigate the headless browser to a URL. Returns page title and final URL.",
    {
        "url":         {"type": "string", "description": "URL to navigate to"},
        "wait_until":  {"type": "string", "description": "Playwright wait condition: load|domcontentloaded|networkidle", "default": "domcontentloaded"},
        "timeout_ms":  {"type": "integer", "description": "Navigation timeout in milliseconds", "default": 15000},
    },
)
async def _playwright_navigate(args: dict[str, Any]) -> dict:
    url = args.get("url", "")
    if not url:
        return sdk_error("url is required")
    wait_until = args.get("wait_until", "domcontentloaded")
    timeout_ms = int(args.get("timeout_ms", 15000))
    try:
        page = await _ensure_page()
        response = await page.goto(url, wait_until=wait_until, timeout=timeout_ms)
        title = await page.title()
        return sdk_result({
            "url": page.url,
            "title": title,
            "status": response.status if response else None,
        })
    except ImportError:
        return sdk_error("playwright is not installed. Run: uv add playwright && playwright install chromium")
    except Exception as exc:
        logger.warning("playwright_navigate error: %s", exc)
        return sdk_error(f"navigation failed: {exc}")


# ---------------------------------------------------------------------------
# Tool: playwright_inject_prompt
# ---------------------------------------------------------------------------
@tool(
    "playwright_inject_prompt",
    "Navigate to a web LLM URL, inject a prompt into the input field, and optionally submit it.",
    {
        "url":      {"type": "string", "description": "Web LLM URL (claude.ai, chat.openai.com, grok.com, …)"},
        "prompt":   {"type": "string", "description": "Prompt text to inject"},
        "selector": {"type": "string", "description": "CSS selector for the input field (auto-detected from URL if omitted)"},
        "submit":   {"type": "boolean", "description": "Press Enter to submit after injection (default: false)"},
        "timeout_ms": {"type": "integer", "description": "Navigation timeout in ms", "default": 20000},
    },
)
async def _playwright_inject_prompt(args: dict[str, Any]) -> dict:
    url     = args.get("url", "")
    prompt  = args.get("prompt", "")
    submit  = bool(args.get("submit", False))
    timeout = int(args.get("timeout_ms", 20000))
    selector = args.get("selector") or _selector_for(url)

    if not url:
        return sdk_error("url is required")
    if not prompt:
        return sdk_error("prompt is required")
    if not selector:
        return sdk_error(
            "selector is required — auto-detection failed for this URL. "
            "Pass 'selector' explicitly (e.g. 'textarea', 'div[contenteditable]')."
        )

    try:
        page = await _ensure_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        await page.wait_for_selector(selector, timeout=10000)
        await page.fill(selector, prompt)
        if submit:
            await page.press(selector, "Enter")
            await asyncio.sleep(1.5)
        return sdk_result({
            "url": page.url,
            "injected": len(prompt),
            "submitted": submit,
            "selector": selector,
        })
    except ImportError:
        return sdk_error("playwright is not installed. Run: uv add playwright && playwright install chromium")
    except Exception as exc:
        logger.warning("playwright_inject_prompt error: %s", exc)
        return sdk_error(f"inject failed: {exc}")


# ---------------------------------------------------------------------------
# Tool: playwright_screenshot
# ---------------------------------------------------------------------------
@tool(
    "playwright_screenshot",
    "Capture a screenshot of the current browser page (or navigate first). Returns base64 PNG.",
    {
        "url":        {"type": "string", "description": "Optional URL to navigate to before capturing"},
        "full_page":  {"type": "boolean", "description": "Capture full scrollable page (default: false)"},
        "timeout_ms": {"type": "integer", "description": "Navigation timeout in ms", "default": 15000},
    },
)
async def _playwright_screenshot(args: dict[str, Any]) -> dict:
    url       = args.get("url")
    full_page = bool(args.get("full_page", False))
    timeout   = int(args.get("timeout_ms", 15000))
    try:
        page = await _ensure_page()
        if url:
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        png = await page.screenshot(full_page=full_page, type="png")
        return sdk_result({
            "url": page.url,
            "title": await page.title(),
            "screenshot_b64": base64.b64encode(png).decode(),
            "size_bytes": len(png),
        })
    except ImportError:
        return sdk_error("playwright is not installed. Run: uv add playwright && playwright install chromium")
    except Exception as exc:
        logger.warning("playwright_screenshot error: %s", exc)
        return sdk_error(f"screenshot failed: {exc}")


# ---------------------------------------------------------------------------
# Tool: playwright_get_text
# ---------------------------------------------------------------------------
@tool(
    "playwright_get_text",
    "Extract visible text content from the current page or a specific element.",
    {
        "url":      {"type": "string", "description": "Optional URL to navigate to first"},
        "selector": {"type": "string", "description": "CSS selector to extract text from (omit for full page)"},
        "timeout_ms": {"type": "integer", "description": "Navigation timeout in ms", "default": 15000},
    },
)
async def _playwright_get_text(args: dict[str, Any]) -> dict:
    url      = args.get("url")
    selector = args.get("selector")
    timeout  = int(args.get("timeout_ms", 15000))
    try:
        page = await _ensure_page()
        if url:
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        if selector:
            el = page.locator(selector).first
            text = await el.inner_text(timeout=5000)
        else:
            text = await page.inner_text("body")
        return sdk_result({
            "url": page.url,
            "selector": selector,
            "text": text[:8000],  # cap to avoid context flood
            "truncated": len(text) > 8000,
        })
    except ImportError:
        return sdk_error("playwright is not installed. Run: uv add playwright && playwright install chromium")
    except Exception as exc:
        logger.warning("playwright_get_text error: %s", exc)
        return sdk_error(f"get_text failed: {exc}")


ALL_TOOLS = [
    _playwright_navigate,
    _playwright_inject_prompt,
    _playwright_screenshot,
    _playwright_get_text,
]
