---
description: 'Hook executed when a cybersec agent finishes — calculates duration, collects stats, and logs completion.'
---

# AgentEnd Hook – CyberSec Plugin

**Trigger:** When any investigation agent completes work (via `hooks.json → AgentEnd`)

**Input (stdin JSON):**
```json
{"agent_name": "Hunter_Elite", "session_id": "sess-abc123"}
```
*Falls back to `.agent_active.json` state file written by AgentStart.*

**Purpose:**  
Close the agent's work cycle — calculate how long it ran, count what it produced, and log everything.

## What this hook does

1. Reads agent name from stdin JSON, env var, or `.agent_active.json` state
2. Calculates duration since AgentStart
3. Counts session findings, IOCs, and timeline entries
4. Appends `agent_end` entry to session `timeline.md` with stats
5. Logs completion to project `session_changes.log`
6. Cleans up `.agent_active.json` state file

## Output (stdout JSON)

```json
{
  "status": "success",
  "agent_name": "Hunter_Elite",
  "duration": "4m 32s",
  "end_time": "2026-04-05T14:32:00",
  "session_id": "sess-abc123",
  "stats": {"findings": 3, "iocs": 7, "timeline_entries": 12},
  "message": "Agent Hunter_Elite finished after 4m 32s. 3 findings, 7 IOCs this run."
}
```

**Paired with AgentStart hook. Must always fire after AgentStart for accurate tracking.**

