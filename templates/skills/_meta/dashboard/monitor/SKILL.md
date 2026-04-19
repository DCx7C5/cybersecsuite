---
name: dashboard-monitor
description: Generates a self-contained static HTML dashboard showing DB health, active mode (blue/red/purple), intel table counts, session overview, active skills, and settings summary. Run generate_dashboard.py or manage.py dashboard to produce index.html.
model: sonnet
maxTurns: 10
tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - cybersec
tags:
- ops
- dashboard
mitre_attack:
- T1059.004
nist_csf: []
capec: []
---

# Dashboard Skill — CyberSec Health & Status Monitor

**Purpose:**  
Generates a single self-contained `index.html` file with live data baked in.  
Shows DB health, active mode, all intel row counts, table list, settings summary and recent sessions at a glance.

---

## Usage

```bash
# Generate static dashboard (writes skills/dashboard/index.html)
python3 skills/dashboard/generate_dashboard.py

# Generate + immediately open in browser
python3 skills/dashboard/generate_dashboard.py --open

# Generate + serve with live auto-refresh (default port 8322)
python3 skills/dashboard/generate_dashboard.py --serve

# Custom port
python3 skills/dashboard/generate_dashboard.py --serve --port 9000
```

Or via manage.py:
```bash
python3 manage.py dashboard          # generate only
python3 manage.py dashboard --open   # generate + open
python3 manage.py dashboard --serve  # generate + serve
```

---

## What the Dashboard Shows

| Section             | Content                                                                                                                                    |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| **Mode Badge**      | Blue / Red / Purple team with colour coding                                                                                                |
| **DB Status**       | Connected ✓ / Error ✗, PostgreSQL version                                                                                                  |
| **Intel Counts**    | CVEs, CWEs, CAPEC, MITRE techniques, threat actors, software families, MISP events/attributes, OpenCTI indicators/entities, feed snapshots |
| **DB Tables**       | All public tables, total count                                                                                                             |
| **Settings**        | Agent model, phases, flags (non-destructive, IOC logging, MITRE mapping)                                                                   |
| **Active Skills**   | Which skills are enabled in settings.json                                                                                                  |
| **Sessions**        | Recent cybersec-sessions/ directories                                                                                                      |
| **Last Intel Sync** | Timestamp from data/cybersec-shared/meta/                                                                                                  |

---

## Output

- **`skills/dashboard/index.html`** — fully self-contained, no external dependencies.  
  All CSS and JS is inline. Data is embedded as a `<script>` JSON block.

---

## Refresh

- Static file: re-run `generate_dashboard.py` to refresh data.
- `--serve` mode: dashboard auto-refreshes every **30 seconds** via `<meta http-equiv="refresh">`.

