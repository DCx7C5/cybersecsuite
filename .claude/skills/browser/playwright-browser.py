#!/usr/bin/env python3
"""
Playwright Browser Automation for Claude CyberSec Plugin
Modern, high-performance browser control (Chromium/Brave) with advanced forensic features.
"""
import sys
import json
import os
import asyncio
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

async def main_async():
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Usage: python3 playwright-browser.py <action> [arguments...]"
        }))
        print("\nAvailable actions:")
        print("  navigate <url>")
        print("  screenshot [filename]")
        print("  fullpage")
        print("  get-cookies")
        print("  dump-storage")
        print("  extract-links")
        print("  execute-js <javascript>")
        print("  click <css-selector>")
        print("  type <css-selector> <text>")
        print("  get-text <css-selector>")
        print("  scroll-to-bottom")
        print("  stealth")
        sys.exit(1)

    action = sys.argv[1].lower()
    args = sys.argv[2:]

    # Session directory (compatible with your existing plugin)
    session_dir = os.environ.get("CYBERSEC_SESSION_DIR")
    if not session_dir:
        session_dir = Path.home() / "Projects/MalwareHunter/malwarehunter_sessions" / datetime.now().strftime("%Y%m%d_%H%M%S")
    else:
        session_dir = Path(session_dir)
    
    browser_dir = session_dir / "artefacts" / "browser"
    browser_dir.mkdir(parents=True, exist_ok=True)

    try:
        async with async_playwright() as p:
            # Use Chromium (Brave is Chromium-based)
            browser = await p.chromium.launch(
                headless=False,  # Visible by default for forensics
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            result = {"status": "success", "action": action, "timestamp": datetime.now().isoformat()}

            if action == "navigate":
                url = args[0]
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)
                result["url"] = url
                result["title"] = await page.title()

            elif action == "screenshot" or action == "fullpage":
                if args:
                    filename = args[0]
                else:
                    filename = f"screenshot_{datetime.now().strftime('%H%M%S')}.png"
                path = browser_dir / filename
                if action == "fullpage":
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(1000)
                await page.screenshot(path=str(path))
                result["file"] = str(path)

            elif action == "get-cookies":
                cookies = await context.cookies()
                result["cookies"] = cookies
                cookies_path = browser_dir / f"cookies_{datetime.now().strftime('%H%M%S')}.json"
                cookies_path.write_text(json.dumps(cookies, indent=2), encoding="utf-8")
                result["saved_to"] = str(cookies_path)

            elif action == "dump-storage":
                local = await page.evaluate("() => Object.entries(localStorage)")
                session = await page.evaluate("() => Object.entries(sessionStorage)")
                result["localStorage"] = local
                result["sessionStorage"] = session

            elif action == "extract-links":
                links = await page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a[href]')).map(a => a.href);
                }""")
                result["links"] = links

            elif action == "execute-js":
                script = " ".join(args)
                result["result"] = await page.evaluate(script)

            elif action == "click":
                selector = args[0]
                await page.click(selector, timeout=10000)
                result["clicked"] = selector

            elif action == "type":
                selector = args[0]
                text = " ".join(args[1:])
                await page.fill(selector, text)
                result["typed"] = text

            elif action == "get-text":
                selector = args[0]
                text = await page.text_content(selector)
                result["text"] = text

            elif action == "scroll-to-bottom":
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1500)

            elif action == "stealth":
                # Basic stealth
                await page.evaluate("""() => {
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                }""")
                result["stealth"] = "applied"

            print(json.dumps(result))

            # Keep browser open for manual inspection
            print(f"✅ Browser is open and ready. Close it manually when finished.")

            # Do not close browser automatically
            await asyncio.sleep(999999)  # Keep alive

    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()