"""Playwright browser automation tools for cybersec MCP server (T029).

Provides headless browser automation for forensic web-LLM interaction:
    playwright_navigate      — navigate to a URL
    playwright_inject_prompt — open a web LLM and inject a prompt
    playwright_screenshot    — capture a screenshot (base64 PNG)
    playwright_get_text      — extract visible text / element text
    select_element           — select element by CSS or XPath
    fill_form                — fill multiple form fields
    click_element            — click element and wait for navigation
    get_page_content         — retrieve page HTML or element HTML
    get_console_logs         — retrieve JS console output with error traces

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
import time
from dataclasses import dataclass
from typing import Any

from ..sdk_compat import tool
from ..helpers import sdk_result, sdk_error

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


# ---------------------------------------------------------------------------
# Enhanced T029 Tools: Element Selection, Form Filling, Clicking, Content Retrieval
# ---------------------------------------------------------------------------


@tool(
    "select_element",
    "Select an element on the current page using CSS selector or XPath strategy.",
    {
        "selector":  {"type": "string", "description": "Element selector (CSS or XPath)"},
        "strategy":  {"type": "string", "description": "Selector strategy: css or xpath (default: css)"},
        "wait_ms":   {"type": "integer", "description": "Wait for element timeout in ms", "default": 5000},
    },
)
async def _select_element(args: dict[str, Any]) -> dict:
    """
    Select an element on the page by CSS selector or XPath.
    
    Returns element properties (tag name, classes, id, visible text) for validation
    before performing actions like fill or click.
    """
    selector = args.get("selector", "")
    strategy = args.get("strategy", "css").lower()
    wait_ms = int(args.get("wait_ms", 5000))
    
    if not selector:
        return sdk_error("selector is required")
    if strategy not in ("css", "xpath"):
        return sdk_error(f"strategy must be 'css' or 'xpath', got '{strategy}'")
    
    try:
        page = await _ensure_page()
        
        # Wait for element to be present
        if strategy == "css":
            locator = page.locator(selector)
        else:
            locator = page.locator(f"xpath={selector}")
        
        await locator.first.wait_for(timeout=wait_ms)
        
        # Extract element properties
        tag_name = await locator.first.evaluate("el => el.tagName.toLowerCase()")
        classes = await locator.first.evaluate("el => el.className")
        element_id = await locator.first.evaluate("el => el.id")
        visible_text = await locator.first.inner_text()
        is_visible = await locator.first.is_visible()
        is_enabled = await locator.first.is_enabled()
        
        return sdk_result({
            "selector": selector,
            "strategy": strategy,
            "tag": tag_name,
            "id": element_id,
            "classes": classes,
            "visible_text": visible_text[:200],
            "is_visible": is_visible,
            "is_enabled": is_enabled,
            "found": True,
        })
    except ImportError:
        return sdk_error("playwright is not installed. Run: uv add playwright && playwright install chromium")
    except Exception as exc:
        logger.warning("select_element error: %s", exc)
        return sdk_error(f"element selection failed: {exc}")


@tool(
    "fill_form",
    "Fill multiple form fields on the current page.",
    {
        "elements": {
            "type": "object",
            "description": "Dict mapping CSS selectors to values: {'#email': 'user@example.com', '#password': 'pass123'}",
        },
        "clear_first": {
            "type": "boolean",
            "description": "Clear field before filling (default: true)",
            "default": True,
        },
        "wait_ms": {
            "type": "integer",
            "description": "Wait timeout in ms for each field",
            "default": 3000,
        },
    },
)
async def _fill_form(args: dict[str, Any]) -> dict:
    """
    Fill multiple form fields identified by CSS selectors.
    
    Useful for login forms, search boxes, or multi-field inputs.
    Returns success count and any errors encountered.
    """
    elements = args.get("elements", {})
    clear_first = bool(args.get("clear_first", True))
    wait_ms = int(args.get("wait_ms", 3000))
    
    if not elements or not isinstance(elements, dict):
        return sdk_error("elements must be a non-empty dict mapping selectors to values")
    
    try:
        page = await _ensure_page()
        results = {"filled": 0, "failed": 0, "errors": []}
        
        for selector, value in elements.items():
            try:
                locator = page.locator(selector)
                await locator.first.wait_for(timeout=wait_ms)
                
                if clear_first:
                    await locator.first.clear()
                
                await locator.first.fill(str(value))
                results["filled"] += 1
            except Exception as exc:
                results["failed"] += 1
                results["errors"].append(f"{selector}: {str(exc)[:100]}")
        
        return sdk_result({
            "filled": results["filled"],
            "failed": results["failed"],
            "total": len(elements),
            "errors": results["errors"],
        })
    except ImportError:
        return sdk_error("playwright is not installed. Run: uv add playwright && playwright install chromium")
    except Exception as exc:
        logger.warning("fill_form error: %s", exc)
        return sdk_error(f"form filling failed: {exc}")


@tool(
    "click_element",
    "Click an element on the current page.",
    {
        "selector":  {"type": "string", "description": "CSS selector for the element to click"},
        "wait_ms":   {"type": "integer", "description": "Wait timeout in ms", "default": 3000},
        "wait_after_click_ms": {
            "type": "integer",
            "description": "Wait after clicking in ms (for page load/navigation)",
            "default": 500,
        },
    },
)
async def _click_element(args: dict[str, Any]) -> dict:
    """
    Click an element on the page and optionally wait for navigation/load.
    
    Useful for form submission, button clicks, or link navigation.
    """
    selector = args.get("selector", "")
    wait_ms = int(args.get("wait_ms", 3000))
    wait_after_click_ms = int(args.get("wait_after_click_ms", 500))
    
    if not selector:
        return sdk_error("selector is required")
    
    try:
        page = await _ensure_page()
        locator = page.locator(selector)
        
        # Wait for element and click
        await locator.first.wait_for(timeout=wait_ms)
        await locator.first.click()
        
        # Wait for potential navigation
        if wait_after_click_ms > 0:
            await asyncio.sleep(wait_after_click_ms / 1000.0)
        
        return sdk_result({
            "selector": selector,
            "clicked": True,
            "url": page.url,
            "title": await page.title(),
        })
    except ImportError:
        return sdk_error("playwright is not installed. Run: uv add playwright && playwright install chromium")
    except Exception as exc:
        logger.warning("click_element error: %s", exc)
        return sdk_error(f"click failed: {exc}")


@tool(
    "screenshot",
    "Capture a screenshot of the current browser page.",
    {
        "full_page":  {"type": "boolean", "description": "Capture full scrollable page (default: false)"},
        "selector":   {"type": "string", "description": "Optional element selector to screenshot (default: entire page)"},
        "timeout_ms": {"type": "integer", "description": "Wait timeout in ms", "default": 5000},
    },
)
async def _screenshot_operation(args: dict[str, Any]) -> dict:
    """
    Capture a screenshot of the page or a specific element.
    
    Returns base64-encoded PNG data suitable for embedding in dashboards.
    """
    full_page = bool(args.get("full_page", False))
    selector = args.get("selector")
    timeout_ms = int(args.get("timeout_ms", 5000))
    
    try:
        page = await _ensure_page()
        
        if selector:
            # Screenshot specific element
            locator = page.locator(selector)
            await locator.first.wait_for(timeout=timeout_ms)
            png = await locator.first.screenshot(type="png")
        else:
            # Screenshot entire page or viewport
            png = await page.screenshot(full_page=full_page, type="png")
        
        return sdk_result({
            "url": page.url,
            "title": await page.title(),
            "screenshot_b64": base64.b64encode(png).decode(),
            "size_bytes": len(png),
            "selector": selector or "full_page" if full_page else "viewport",
        })
    except ImportError:
        return sdk_error("playwright is not installed. Run: uv add playwright && playwright install chromium")
    except Exception as exc:
        logger.warning("screenshot error: %s", exc)
        return sdk_error(f"screenshot failed: {exc}")


@tool(
    "get_page_content",
    "Retrieve the full HTML content of the current page or a specific element.",
    {
        "selector": {
            "type": "string",
            "description": "Optional CSS selector to get element HTML (default: entire page)",
        },
        "max_chars": {
            "type": "integer",
            "description": "Maximum characters to return (default: 50000)",
            "default": 50000,
        },
    },
)
async def _get_page_content(args: dict[str, Any]) -> dict:
    """
    Retrieve page HTML or element HTML content.
    
    Useful for parsing page structure, finding elements, or validating page state.
    """
    selector = args.get("selector")
    max_chars = int(args.get("max_chars", 50000))
    
    try:
        page = await _ensure_page()
        
        if selector:
            # Get specific element HTML
            locator = page.locator(selector)
            html_content = await locator.first.inner_html()
            content_type = "element_html"
        else:
            # Get full page HTML
            html_content = await page.content()
            content_type = "full_page_html"
        
        # Truncate if necessary
        truncated = len(html_content) > max_chars
        if truncated:
            html_content = html_content[:max_chars]
        
        return sdk_result({
            "url": page.url,
            "selector": selector or "full_page",
            "content_type": content_type,
            "content": html_content,
            "char_count": len(html_content),
            "truncated": truncated,
        })
    except ImportError:
        return sdk_error("playwright is not installed. Run: uv add playwright && playwright install chromium")
    except Exception as exc:
        logger.warning("get_page_content error: %s", exc)
        return sdk_error(f"get_page_content failed: {exc}")


# ---------------------------------------------------------------------------
# Console Logging Buffer (T029: get_console_logs)
# In-memory circular buffer for JS console output with timestamps and types
# ---------------------------------------------------------------------------

@dataclass
class _ConsoleMessage:
    """Single console message with metadata."""
    timestamp: float
    message_type: str  # 'log', 'error', 'warning', 'info'
    text: str
    args: list[str]
    stack_trace: str | None = None
    url: str = ""


_console_buffer: list[_ConsoleMessage] = []
_console_buffer_max = 100
_console_buffer_lock = asyncio.Lock()


async def _console_handler(msg: Any) -> None:
    """Handle console.log, console.error, etc. from page context."""
    global _console_buffer
    
    msg_type = msg.type or "log"
    text = msg.text or ""
    args = msg.args or []
    
    # Extract stack trace if available (for errors)
    stack_trace = None
    if msg_type == "error" and hasattr(msg, 'stack_trace'):
        stack_trace = str(msg.stack_trace)
    
    async with _console_buffer_lock:
        console_msg = _ConsoleMessage(
            timestamp=time.time(),
            message_type=msg_type,
            text=text,
            args=[str(arg) for arg in args[:10]],  # Cap args
            stack_trace=stack_trace,
            url=_page.url if _page else "",
        )
        _console_buffer.append(console_msg)
        
        # Maintain circular buffer
        if len(_console_buffer) > _console_buffer_max:
            _console_buffer = _console_buffer[-_console_buffer_max:]


async def _setup_console_logging() -> None:
    """Install console logging handler on the page."""
    try:
        page = await _ensure_page()
        page.on("console", _console_handler)
        logger.debug("Console logging installed on browser page")
    except Exception as exc:
        logger.warning("Failed to install console logging: %s", exc)


@tool(
    "get_console_logs",
    "Retrieve JavaScript console output from the browser (logs, errors, warnings).",
    {
        "message_type": {
            "type": "string",
            "description": "Filter by type: log|error|warning|info|all (default: all)",
            "default": "all",
        },
        "limit": {
            "type": "integer",
            "description": "Maximum messages to return (default: 50)",
            "default": 50,
        },
    },
)
async def _get_console_logs(args: dict[str, Any]) -> dict:
    """
    Retrieve JavaScript console output from the browser page.
    
    Supports filtering by message type and returns timestamped output
    with error stack traces when available. Useful for debugging
    JavaScript errors during web LLM interaction or form automation.
    
    Returns:
        - timestamp: Unix timestamp when message was logged
        - type: 'log', 'error', 'warning', 'info'
        - text: Main console message
        - args: Additional arguments passed to console.*
        - stack_trace: Stack trace (for errors)
        - url: Page URL where message originated
    """
    message_type = args.get("message_type", "all").lower()
    limit = max(1, min(int(args.get("limit", 50)), 500))
    
    if message_type not in ("log", "error", "warning", "info", "all"):
        return sdk_error(
            f"message_type must be 'log'|'error'|'warning'|'info'|'all', got '{message_type}'"
        )
    
    try:
        # Ensure page exists and console logging is setup
        await _ensure_page()
        if not any(cb for cb in _page._listeners.get("console", []) if callable(cb)):
            await _setup_console_logging()
        
        async with _console_buffer_lock:
            # Filter messages
            if message_type == "all":
                filtered = _console_buffer
            else:
                filtered = [m for m in _console_buffer if m.message_type == message_type]
            
            # Get last N messages
            recent = filtered[-limit:] if filtered else []
            
            # Format for output
            formatted_logs = []
            for msg in recent:
                formatted_logs.append({
                    "timestamp": msg.timestamp,
                    "type": msg.message_type,
                    "text": msg.text,
                    "args": msg.args,
                    "stack_trace": msg.stack_trace,
                    "url": msg.url,
                })
            
            return sdk_result({
                "message_type": message_type,
                "count": len(formatted_logs),
                "total_buffered": len(_console_buffer),
                "logs": formatted_logs,
            })
    except ImportError:
        return sdk_error("playwright is not installed. Run: uv add playwright && playwright install chromium")
    except Exception as exc:
        logger.warning("get_console_logs error: %s", exc)
        return sdk_error(f"console logging retrieval failed: {exc}")


# Updated ALL_TOOLS including new T029 operations
ALL_TOOLS = [
    _playwright_navigate,
    _playwright_inject_prompt,
    _playwright_screenshot,
    _playwright_get_text,
    _select_element,
    _fill_form,
    _click_element,
    _screenshot_operation,
    _get_page_content,
    _get_console_logs,
]
