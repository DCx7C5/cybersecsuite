#!/usr/bin/env python3
"""Playwright Stealth MCP Server - Production-ready browser automation with anti-detection."""
import asyncio
import base64
import os
import random
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from playwright.async_api import async_playwright, Page, BrowserContext
from playwright_stealth import Stealth

from config import get_brave_path, USER_DATA_DIR
from utils import get_minimal_state


# Initialize FastMCP
mcp = FastMCP("playwright-stealth")

# Global browser state
_browser_context: BrowserContext | None = None
_page: Page | None = None


@asynccontextmanager
async def browser_lifespan():
    """Manage browser lifecycle."""
    global _browser_context, _page

    user_data_dir = os.getenv("USER_DATA_DIR", USER_DATA_DIR)
    brave_path = get_brave_path()

    async with async_playwright() as p:
        _browser_context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            executable_path=brave_path,
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--mute-audio",
            ],
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="Europe/Berlin",
            java_script_enabled=True,
            permissions=[],
        )

        _page = _browser_context.pages[0] if _browser_context.pages else await _browser_context.new_page()
        stealth_config = Stealth()
        await stealth_config.apply_stealth_async(_page)

        # Fingerprint blocking script
        await _browser_context.add_init_script("""
            const origGetContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type, ...args) {
                const ctx = origGetContext.call(this, type, ...args);
                if (ctx && (type === '2d' || type.includes('webgl'))) {
                    const origGetImageData = ctx.getImageData;
                    ctx.getImageData = function(x, y, w, h) {
                        const data = origGetImageData.call(this, x, y, w, h);
                        for (let i = 0; i < data.data.length; i += 4) {
                            data.data[i] ^= Math.floor(Math.random() * 3);
                        }
                        return data;
                    };
                }
                return ctx;
            };

            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
            Object.defineProperty(navigator, 'plugins', { get: () => [] });
        """)

        print(f"✅ Brave Stealth MCP started (Profile: {user_data_dir})")

        try:
            yield
        finally:
            await _browser_context.close()


# Navigation tool
@mcp.tool()
async def navigate(url: str) -> dict:
    """Navigate to URL with stealth mode."""
    if _page is None:
        raise RuntimeError("Browser not initialized")
    await _page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await _page.wait_for_timeout(1000)
    return await get_minimal_state(_page)


# Interaction tools
@mcp.tool()
async def click(selector: str) -> dict:
    """Click element with human-like delay."""
    if _page is None:
        raise RuntimeError("Browser not initialized")
    await _page.wait_for_selector(selector, timeout=10000)
    await _page.click(selector, delay=random.randint(50, 150))
    await _page.wait_for_timeout(random.randint(600, 1200))
    return await get_minimal_state(_page)


@mcp.tool()
async def type_text(selector: str, text: str) -> dict:
    """Type text with human-like typing."""
    if _page is None:
        raise RuntimeError("Browser not initialized")
    await _page.wait_for_selector(selector, timeout=10000)
    await _page.fill(selector, "")
    for char in text:
        await _page.type(selector, char, delay=random.randint(30, 120))
    await _page.wait_for_timeout(random.randint(400, 900))
    return await get_minimal_state(_page)


# Heavy tools (high token cost)
@mcp.tool()
async def get_full_html() -> dict:
    """Get full page HTML (high token cost - use only when needed)."""
    if _page is None:
        raise RuntimeError("Browser not initialized")
    return {"type": "tool_result", "content": {"html": await _page.content()}}


@mcp.tool()
async def take_screenshot() -> dict:
    """Take screenshot as base64 (high token cost)."""
    if _page is None:
        raise RuntimeError("Browser not initialized")
    screenshot = await _page.screenshot(full_page=True)
    return {
        "type": "tool_result",
        "content": {"screenshot_base64": base64.b64encode(screenshot).decode()}
    }


async def main():
    """Main entry point with browser lifecycle."""
    async with browser_lifespan():
        # Run MCP server
        await mcp.run_async(transport="stdio")


if __name__ == "__main__":
    asyncio.run(main())

