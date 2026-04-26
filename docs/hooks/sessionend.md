---
description: 'Hook executed automatically on every cybersec session end – syncs findings to shared memory and finalizes artefacts.'
---

# SessionEnd Hook – CyberSec Plugin

**Trigger:** End of every investigation session

**Purpose:**  
Guarantee **nothing is lost** between sessions.

## What this hook does

1. Calls `session_end.py`
2. Syncs `$SESSION_DIR/iocs.md` → `./cybersec-shared/ioc-db.md` (deduplicated + confidence escalation)
3. Updates watchlist, cleared.md, threat-profile.md and baselines
4. Appends entry to `session-index.md`
5. Finalizes `manifest.json` (end_time, status = "complete", ioc_count)
6. Updates timeline.md with final verdict
7. Logs session summary

**All agents must call this hook before ending a session.**

**Do not modify without updating manifest.json + hooks.json**