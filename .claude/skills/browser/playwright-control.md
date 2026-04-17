---
name: playwright-control
description: Advanced Playwright browser automation. High-performance control of Brave browser with many forensic actions: navigate, screenshots, cookies dump, storage extraction, link scraping, JS execution, click, type, scroll, stealth mode, and more.
version: 2.0
---

# Playwright Browser Control Skill

**Purpose:**  
Full, modern browser automation using **Playwright** — faster and more reliable than Selenium. Perfect for forensic analysis, IOC collection, security testing, and automated evidence gathering.

**Key Features:**
- Uses real Brave browser (Chromium)
- Advanced actions (click, type, JS execution, storage dump, etc.)
- Automatic screenshot & page source saving
- All artefacts saved to current session's `artefacts/browser/`
- Stealth capabilities
- Returns clean JSON status

**Available Actions:**
- `navigate <url>`
- `screenshot [filename]`
- `fullpage`
- `get-cookies`
- `dump-storage`
- `extract-links`
- `execute-js <javascript>`
- `click <css-selector>`
- `type <css-selector> <text>`
- `get-text <css-selector>`
- `scroll-to-bottom`
- `stealth`

**Usage:**
```bash
python3 playwright-browser.py navigate https://example.com
python3 playwright-browser.py get-cookies
python3 playwright-browser.py screenshot evidence.png
python3 playwright-browser.py fullpage