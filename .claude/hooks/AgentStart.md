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

## Known Agents

| Agent             | Focus                                            |
|-------------------|--------------------------------------------------|
| Hunter            | General-purpose threat hunting across all layers |
| Hunter_Elite      | APT-level persistence, rootkits, supply-chain    |
| Layer2-Specialist | ARP, MAC, VLAN, switch-level attacks             |
| Layer3-Specialist | IP, routing, ICMP, BGP hijack                    |
| Layer4-Specialist | TCP/UDP, port scans, SYN floods                  |
| Layer5-Specialist | TLS, session hijack, auth tokens                 |
| Layer6-Specialist | Encoding, serialization, crypto                  |
| Layer7-Specialist | HTTP, DNS, API, web app exploits                 |
| Memory-Analyst    | Volatile memory forensics                        |
| Firmware-Analyst  | Firmware extraction, UEFI/BIOS implants          |
| Reverse-Engineer  | Binary analysis, malware RE                      |

**Paired with AgentEnd hook for duration tracking and session stats.**

