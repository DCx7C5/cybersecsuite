---
name: team-task-analyze
description: Route a task to the blue, red, or purple team agent defined in .claude/agents/teams/. Requires CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1. Prints the correct claude invocation for the selected team.
domain: cybersecurity
subdomain: ops
tags:
- team
- blue-team
- red-team
- purple-team
- orchestration
- agent-routing
mitre_attack: []
cve: []
cwe: []
nist_csf: []
capec: []
---
## Overview

Slash-command dispatcher that routes a natural-language task to the appropriate team agent. Maps team name to `.claude/agents/teams/{team}-team.md` and prints the correct `claude --agent` invocation. Requires the experimental agent-teams feature flag.

## Usage

```
/team-task blue   "Hunt for lateral movement indicators in auth.log"
/team-task red    "Enumerate attack surface of 192.168.1.0/24"
/team-task purple "Validate detection coverage for T1059.001 PowerShell"
```

## Teams

| Team | Mode | Agent file |
|---|---|---|
| `blue` | Defensive: threat hunting, IR, log analysis, hardening | `agents/teams/blue-team.md` |
| `red` | Offensive: recon, exploitation, persistence, C2 | `agents/teams/red-team.md` |
| `purple` | Combined: ATT&CK validation, detection coverage mapping | `agents/teams/purple-team.md` |

## Requirements

- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` set in `settings.json` (or env)
- Team agent files present in `.claude/agents/teams/`
- Pair with `mode-switch` to set the appropriate operational mode before tasking
