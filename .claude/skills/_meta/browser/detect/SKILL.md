---
name: browser-detect
description: Browser forensic reconnaissance for Chromium/Firefox/Brave artifacts, extensions, history, cookies, IndexedDB, saved credentials, and session theft detection. Covers Playwright/Selenium automation and SSLKEYLOG TLS correlation.
model: sonnet
maxTurns: 30
tools:
  - Read
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
skills:
  - shared-memory
  - tls/sslkeylog
  - network/recon
  - threats/mitre-attack-mapper
tags:
- ops
- browser
mitre_attack:
- T1003
- T1059
- T1595
nist_csf: []
capec: []
---

# Browser Forensic Recon

**Purpose:** Deep forensic triage of browser artifacts, credentials, sessions, extensions, and network activity. Detects browser-based compromise, session hijacking, credential harvesting, and malicious extensions.

---

## Core Focus Areas

- **Profile forensics**: History, bookmarks, downloads, cache, cookies, IndexedDB, Web SQL, localStorage, sessionStorage
- **Credential stores**: Saved passwords (Chromium `Login Data`, Firefox `logins.json`), master password analysis
- **Session theft indicators**: Cookie exfiltration artifacts, OAuth token stores, session-fixation patterns
- **Extension analysis**: Installed extensions, dangerous permissions (`<all_urls>`, `nativeMessaging`, `debugger`), background scripts
- **TLS/HTTPS artifacts**: Accepted certificate errors, HSTS bypass indicators, SSLKEYLOGFILE correlation
- **Download artifacts**: Downloaded file hashes, suspicious MIME types, drive-by download traces
- **Browser process memory**: Injected code regions, unusual child processes, credential dumps from heap

---

## Key Techniques & Tools

### Profile Discovery
```bash
# All Chromium-family profiles
find /home /root -type d -name "Default" \
  \( -path "*/chromium/*" -o -path "*/google-chrome/*" \
     -o -path "*/BraveSoftware/*" -o -path "*/microsoft-edge/*" \) 2>/dev/null

# Firefox profiles
find /home /root -maxdepth 6 -name "*.default*" \
  -path "*/.mozilla/firefox/*" 2>/dev/null

# Chrome/Brave on Flatpak
find /home -path "*/.var/app/*/config/*/Default" 2>/dev/null
```

### History & Downloads
```bash
# Chromium history (SQLite) — last 50 visits
for db in $(find /home /root -name "History" -path "*/Default/*" 2>/dev/null); do
  echo "=== $db ==="
  sqlite3 "$db" "SELECT datetime(last_visit_time/1000000-11644473600,'unixepoch'),
    url, title FROM urls ORDER BY last_visit_time DESC LIMIT 50;" 2>/dev/null
done

# Chromium downloads
sqlite3 ~/.config/chromium/Default/History \
  "SELECT datetime(start_time/1000000-11644473600,'unixepoch'),
    target_path, tab_url, total_bytes, danger_type
   FROM downloads ORDER BY start_time DESC LIMIT 30;" 2>/dev/null

# Firefox history
sqlite3 ~/.mozilla/firefox/*.default*/places.sqlite \
  "SELECT datetime(last_visit_date/1000000,'unixepoch'), url, title
   FROM moz_places ORDER BY last_visit_date DESC LIMIT 50;" 2>/dev/null

# Firefox downloads (moz_annos)
sqlite3 ~/.mozilla/firefox/*.default*/places.sqlite \
  "SELECT p.url, a.content, datetime(a.lastModified/1000000,'unixepoch')
   FROM moz_annos a JOIN moz_places p ON a.place_id=p.id
   WHERE a.anno_attribute_id IN
     (SELECT id FROM moz_anno_attributes WHERE name LIKE '%download%')
   ORDER BY a.lastModified DESC LIMIT 20;" 2>/dev/null
```

### Cookie & Session Analysis
```bash
# Chromium cookies — session and persistent
sqlite3 ~/.config/chromium/Default/Cookies \
  "SELECT host_key, name, value,
     datetime(expires_utc/1000000-11644473600,'unixepoch'),
     is_secure, is_httponly, samesite
   FROM cookies ORDER BY last_access_utc DESC LIMIT 50;" 2>/dev/null

# Firefox cookies
sqlite3 ~/.mozilla/firefox/*.default*/cookies.sqlite \
  "SELECT host, name, value, datetime(expiry,'unixepoch'),
     isSecure, isHttpOnly, sameSite
   FROM moz_cookies ORDER BY lastAccessed DESC LIMIT 50;" 2>/dev/null

# High-value session cookies (auth tokens, JWT, PHPSESSID, JSESSIONID)
sqlite3 ~/.config/chromium/Default/Cookies \
  "SELECT host_key, name, value FROM cookies
   WHERE name IN ('session','PHPSESSID','JSESSIONID','auth_token',
     'access_token','refresh_token','remember_me') OR
     value LIKE 'eyJ%';" 2>/dev/null
```

### Extension Audit
```bash
# Chromium extensions — name + dangerous permissions
for ext_dir in ~/.config/chromium/Default/Extensions/*/; do
  manifest=$(find "$ext_dir" -maxdepth 2 -name "manifest.json" | head -1)
  [ -f "$manifest" ] || continue
  name=$(python3 -c "import json; d=json.load(open('$manifest')); print(d.get('name','?'))" 2>/dev/null)
  perms=$(python3 -c "import json; d=json.load(open('$manifest')); \
    p=d.get('permissions',[])+d.get('host_permissions',[]); print(p)" 2>/dev/null)
  echo "EXT: $name"
  echo "  PERMS: $perms"
  echo "  PATH: $ext_dir"
done

# Flag dangerous permissions
grep -rl '"<all_urls>"\|"nativeMessaging"\|"debugger"\|"proxy"\|"webRequest"' \
  ~/.config/chromium/Default/Extensions/ 2>/dev/null | head -20

# Firefox extensions
python3 -c "
import json, sys
data = json.load(open('$HOME/.mozilla/firefox/$(ls ~/.mozilla/firefox/ | grep default | head -1)/extensions.json'))
for e in data.get('addons',[]):
    print(e.get('id','?'), '|', e.get('name','?'), '| active:', e.get('active'))
" 2>/dev/null
```

### Saved Credentials
```bash
# Firefox logins (encrypted with key4.db / NSS)
python3 -c "
import json
logins = json.load(open('$HOME/.mozilla/firefox/$(ls ~/.mozilla/firefox/ | grep default | head -1)/logins.json'))
for l in logins.get('logins',[]):
    print(l.get('hostname'), '|', l.get('encryptedUsername'), '|',
          __import__('datetime').datetime.fromtimestamp(l.get('timeLastUsed',0)/1000))
" 2>/dev/null

# Chromium Login Data (unencrypted usernames visible)
sqlite3 ~/.config/chromium/Default/"Login Data" \
  "SELECT origin_url, username_value,
     datetime(date_created/1000000-11644473600,'unixepoch'),
     times_used
   FROM logins ORDER BY date_used DESC LIMIT 30;" 2>/dev/null

# Brave / Chrome on Linux — check for GNOME Keyring / KWallet entries
secret-tool search --all application chromium 2>/dev/null | head -20
```

### LocalStorage / IndexedDB
```bash
# Chromium LocalStorage
find ~/.config/chromium/Default/Local\ Storage/ -name "*.localstorage" 2>/dev/null | \
  while read f; do
    echo "=== $f ==="
    sqlite3 "$f" "SELECT key, value FROM ItemTable LIMIT 20;" 2>/dev/null
  done

# Chromium IndexedDB — look for token storage
find ~/.config/chromium/Default/IndexedDB/ -name "*.ldb" 2>/dev/null | \
  xargs strings 2>/dev/null | grep -iE "(token|jwt|bearer|oauth|session)" | head -20
```

### SSLKEYLOG Correlation
```bash
# Check active SSLKEYLOGFILE for any browser process
cat /proc/*/environ 2>/dev/null | tr '\0' '\n' | grep SSLKEYLOGFILE | sort -u

# Verify keylog file permissions
[ -n "$SSLKEYLOGFILE" ] && ls -la "$SSLKEYLOGFILE" 2>/dev/null
[ -n "$SSLKEYLOGFILE" ] && wc -l "$SSLKEYLOGFILE" 2>/dev/null
```

### Playwright Automation
```bash
# Browser artifact analysis via Playwright
python3 skills/browser/playwright-browser.py --artifact-dir ./session-artifacts/

# Headless screenshot + network capture
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(record_har_path='/tmp/trace.har')
    page = ctx.new_page()
    page.goto('https://target.local')
    ctx.close(); browser.close()
"
```

---

## MITRE ATT&CK Mapping

| Finding                            | Technique                                 |
|------------------------------------|-------------------------------------------|
| Cookie / session token theft       | T1539 – Steal Web Session Cookie          |
| Saved password extraction          | T1555.003 – Credentials from Web Browsers |
| Malicious extension installed      | T1176 – Browser Extensions                |
| Payload downloaded via browser     | T1105 – Ingress Tool Transfer             |
| Browser process injection          | T1055 – Process Injection                 |
| Browser history exfiltration       | T1217 – Browser Information Discovery     |
| Credential harvesting via phishing | T1056.003 – Web Portal Capture            |

---

## Rules for Agents

1. Never attempt to decrypt NSS/Chromium credentials without explicit `AgentRootPermission` approval
2. Flag any extension with `<all_urls>`, `nativeMessaging`, or `debugger` permission as **MEDIUM+**
3. Log all session cookies for monitored hosts (SHA-256 of value) to `iocs.md`
4. Cross-correlate suspicious download timestamps against network/recon connection log
5. Check SSLKEYLOGFILE — world-readable = **HIGH** immediately
6. Sync all browser IOCs to shared memory at session end
