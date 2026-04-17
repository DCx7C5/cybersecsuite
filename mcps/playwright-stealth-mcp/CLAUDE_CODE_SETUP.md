# Playwright Stealth MCP - Claude Code Integration

## ✅ Server Status: FUNKTIONIERT!

Der Server wurde erfolgreich getestet und läuft:
```
✅ Brave Stealth MCP started (Profile: ../brave_stealth_profile)
🚀 FastMCP 3.1.0
📡 Starting MCP server 'playwright-stealth' with transport 'stdio'
```

## 🔧 Claude Code MCP Konfiguration

Öffne deine Claude Code Settings (`~/.claude/settings.json`) und füge hinzu:

```json
{
  "mcpServers": {
    "playwright-stealth": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/daen/Projects/AI/mcps/playwright-stealth-mcp",
        "run",
        "python",
        "main.py"
      ],
      "env": {
        "ANTHROPIC_AUTH_TOKEN": "cp-1775816175-zlObTy1KFxfOyuqfxi67yQ",
        "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4.6",
        "ANTHROPIC_BASE_URL": "https://localhost:8443/v1",
        "USER_DATA_DIR": "/home/daen/Projects/AI/mcps/playwright-stealth-mcp/brave_profile"
      }
    }
  }
}
```

**💡 Wichtig:** Diese Konfiguration verwendet den Copilot API Proxy (`https://localhost:8443/v1`), 
damit alle MCP-Tool-Aufrufe über deinen Proxy laufen und von GitHub Copilot abgedeckt sind!

## 🛠️ Verfügbare Tools

Nach der Integration stehen dir 5 Tools zur Verfügung:

### 1. `navigate(url: str)`
**Beschreibung:** Navigate zu einer URL mit Stealth-Modus  
**Verwendung:** Websiten besuchen ohne Bot-Detection  
**Token-Cost:** Low

### 2. `click(selector: str)`  
**Beschreibung:** Click auf Element mit menschenähnlichem Delay (50-150ms)  
**Verwendung:** Buttons, Links klicken  
**Token-Cost:** Low

### 3. `type_text(selector: str, text: str)`
**Beschreibung:** Text eingeben mit realistischen Charakter-Delays (30-120ms)  
**Verwendung:** Formulare ausfüllen, Login-Daten eingeben  
**Token-Cost:** Low

### 4. `get_full_html()`
**Beschreibung:** Vollständige HTML der Seite extrahieren  
**Verwendung:** Nur wenn wirklich benötigt (parsen, scraping)  
**Token-Cost:** 🔴 **HIGH** - Vorsicht!

### 5. `take_screenshot()`
**Beschreibung:** Screenshot der Seite als base64  
**Verwendung:** Visuelle Inspektion, Debugging  
**Token-Cost:** 🔴 **HIGH** - Vorsicht!

## 💡 Beispiel-Prompts für Claude Code

```
"Navigate to https://example.com and show me the page title"

"Click on the login button at selector 'button.login-btn'"

"Type 'testuser' into the username field '#username'"

"Go to https://google.com and search for 'playwright stealth'"

"Take a screenshot of the current page"
```

## 🚀 Nach der Integration

1. **Settings.json aktualisieren** (siehe oben)
2. **IDE neustarten** (PyCharm/IntelliJ)
3. **In Claude Code testen:**
   ```
   @playwright-stealth navigate to https://example.com
   ```

## 🔍 Stealth-Features

Der Server bietet automatisch:

✅ **Anti-Bot-Detection:**
- playwright-stealth Plugin aktiv
- Canvas Fingerprinting blockiert
- WebDriver-Flags deaktiviert

✅ **Human-like Behavior:**
- Random Click-Delays (50-150ms)
- Random Type-Delays (30-120ms/char)
- Post-Action Waits (400-1200ms)

✅ **Browser Spoofing:**
- User-Agent: Chrome/Windows
- Navigator: hardwareConcurrency=8, deviceMemory=8
- Timezone: Europe/Berlin, Locale: en-US

## 📊 Server-Test

Testen ob der Server läuft:

```bash
cd /home/daen/Projects/AI/mcps/playwright-stealth-mcp
timeout 5 uv run python main.py
```

**Erwartete Ausgabe:**
```
✅ Brave Stealth MCP started (Profile: ../brave_stealth_profile)
[FastMCP Banner]
INFO Starting MCP server 'playwright-stealth' with transport 'stdio'
```

## ⚙️ Environment Variables (Optional)

```bash
# Eigener Browser-Pfad
export BRAVE_PATH=/usr/bin/brave

# Eigenes User-Data-Directory
export USER_DATA_DIR=./my_brave_profile
```

## 🐛 Troubleshooting

### Server startet nicht in Claude Code

1. **Prüfe Server manuell:**
   ```bash
   cd /home/daen/Projects/AI/mcps/playwright-stealth-mcp
   uv run python main.py
   ```

2. **Prüfe Logs:**
   - Claude Code: IDE Logs ansehen
   - Terminal: Siehe oben

### "Browser not initialized" Fehler

Der Browser startet beim ersten Tool-Aufruf. Das ist normal und dauert 2-3 Sekunden.

### "Failed to launch chromium"

Falls Brave nicht gefunden wird, installiere Chromium:
```bash
sudo pacman -S chromium
```

## ✅ Checkliste Integration

- [ ] `settings.json` mit MCP-Konfiguration aktualisiert
- [ ] IDE neugestartet
- [ ] Test-Prompt gesendet: `@playwright-stealth navigate to https://example.com`
- [ ] Server-Output in IDE-Logs sichtbar
- [ ] Tools erscheinen in Claude Code Auto-Complete

## 🎯 Fertig!

Der Playwright Stealth MCP Server ist jetzt bereit für die Nutzung in Claude Code!

**Happy Browsing! 🚀**

