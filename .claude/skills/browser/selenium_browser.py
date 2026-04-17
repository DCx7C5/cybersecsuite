#!/usr/bin/env python3
"""
Advanced Selenium Browser Automation for Claude CyberSec Plugin
Supports many forensic and security testing actions.
"""
import sys
import json
import os
import time
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Usage: python3 selenium-browser.py <action> [arguments...]"
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
        sys.exit(1)

    action = sys.argv[1].lower()
    args = sys.argv[2:]

    # Session directory (compatible with your existing structure)
    session_dir = os.environ.get("CYBERSEC_SESSION_DIR")
    if not session_dir:
        session_dir = Path.home() / "Projects/MalwareHunter/malwarehunter_sessions" / datetime.now().strftime("%Y%m%d_%H%M%S")
    else:
        session_dir = Path(session_dir)
    
    browser_dir = session_dir / "artefacts" / "browser"
    browser_dir.mkdir(parents=True, exist_ok=True)

    try:
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/brave-browser"
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome(options=chrome_options)

        result = {"status": "success", "action": action, "timestamp": datetime.now().isoformat()}

        if action == "navigate":
            url = args[0]
            driver.get(url)
            time.sleep(3)
            result["url"] = url
            result["title"] = driver.title

        elif action == "screenshot" or action == "fullpage":
            if args:
                filename = args[0]
            else:
                filename = f"screenshot_{datetime.now().strftime('%H%M%S')}.png"
            path = browser_dir / filename
            if action == "fullpage":
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            driver.save_screenshot(str(path))
            result["file"] = str(path)

        elif action == "get-cookies":
            cookies = driver.get_cookies()
            result["cookies"] = cookies
            # Save cookies
            cookies_path = browser_dir / f"cookies_{datetime.now().strftime('%H%M%S')}.json"
            cookies_path.write_text(json.dumps(cookies, indent=2), encoding="utf-8")
            result["saved_to"] = str(cookies_path)

        elif action == "dump-storage":
            local = driver.execute_script("return Object.entries(localStorage);")
            session = driver.execute_script("return Object.entries(sessionStorage);")
            result["localStorage"] = local
            result["sessionStorage"] = session

        elif action == "extract-links":
            links = driver.find_elements(By.TAG_NAME, "a")
            result["links"] = [link.get_attribute("href") for link in links if link.get_attribute("href")]

        elif action == "execute-js":
            script = " ".join(args)
            result["result"] = driver.execute_script(script)

        elif action == "click":
            selector = args[0]
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            result["clicked"] = selector

        elif action == "type":
            selector = args[0]
            text = " ".join(args[1:])
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(text)
            result["typed"] = text

        elif action == "get-text":
            selector = args[0]
            element = driver.find_element(By.CSS_SELECTOR, selector)
            result["text"] = element.text

        elif action == "scroll-to-bottom":
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

    finally:
        # Keep browser open for manual inspection
        print(f"Browser remains open. Close manually when finished.")

if __name__ == "__main__":
    main()