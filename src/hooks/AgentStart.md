---
description: 'Hook executed when a cybersec agent starts — logs agent name, injects profile context, and tracks timing.'
---

# AgentStart Hook – CyberSec Plugin

**Trigger:** When any investigation agent begins work (via `hooks.json → AgentStart`)

**Input (stdin JSON):**
```json
{"agent_name": "Hunter_Elite", "session_id": "sess-abc123"}
```

**Purpose:**  
Track which agent is working, inject agent-specific context, and start the timing clock.

## What this hook does

1. Reads agent name from stdin JSON or `CYBERSEC_AGENT_NAME` env var
2. Writes `.agent_active.json` state file (for AgentEnd to pick up)
3. Appends `agent_start` entry to session `timeline.md`
4. Logs to project `session_changes.log`
5. Injects agent profile + recent findings/IOC summary as `additionalContext`
