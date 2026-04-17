---
name: selenium-control
description: Advanced Selenium browser automation with many forensic and security testing actions (navigate, screenshots, cookies dump, storage dump, link extraction, JS execution, click, type, scroll, etc.)
version: 2.0
---

# Advanced Selenium Control Skill

**Purpose:**  
Full browser automation with advanced actions for forensic analysis, IOC collection, security testing, and dashboard viewing.

**Available Actions:**
- `navigate <url>` – Open any URL
- `screenshot [filename]` – Take screenshot
- `fullpage` – Full page screenshot
- `get-cookies` – Dump all cookies + save to JSON
- `dump-storage` – Extract localStorage + sessionStorage
- `extract-links` – Extract all links on page
- `execute-js <code>` – Run custom JavaScript
- `click <css-selector>` – Click element
- `type <css-selector> <text>` – Type into input
- `get-text <css-selector>` – Get element text
- `scroll-to-bottom` – Scroll page to bottom

**Usage examples:**
```bash
python3 selenium-browser.py navigate https://example.com
python3 selenium-browser.py get-cookies
python3 selenium-browser.py screenshot evidence.png
python3 selenium-browser.py execute-js "console.log('test')"