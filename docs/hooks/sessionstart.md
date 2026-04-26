---
description: 'Hook executed automatically on every cybersec session start – initializes shared memory, artefact logger and loads project context.'
---

# SessionStart Hook – CyberSec Plugin

**Trigger:** Every new investigation session (via `hooks.json`)

**Purpose:**  
Ensure clean, reproducible forensic state before any agent (Hunter, Hunter_Elite, Layer*-Specialist) begins work.

## What this hook does

1. Calls `session_start.py` (already present)
2. Loads `./cybersec-shared/` (IOC-DB, watchlist, cleared items, threat-profile, baselines)
3. Creates new session directory via **artefact-logger** skill
4. Injects full project memory into Claude context (scope, threat model, open findings, risk register)
5. Logs session start in `session.log` + updates `manifest.json`
6. Announces loaded shared memory stats to the analyst

**Ready for Layer 2–7 Specialists, Memory-Analyst and Hunter_Elite.**

**Do not modify without updating manifest.json + hooks.json**