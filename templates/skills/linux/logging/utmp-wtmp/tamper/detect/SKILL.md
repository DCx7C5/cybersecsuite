
---
name: logging-utmp-wtmp-tamper-detect
description: Detect utmp/wtmp login record tampering — identify modifications to /var/run/utmp, /var/log/wtmp, /var/log/btmp used to erase attacker login history.
domain: cybersecurity
subdomain: logging-forensics
tags:
- linux
- utmp
- wtmp
- login
- tamper
- anti-forensics
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1070.006
capec: []
---
# Logging Utmp Wtmp Tamper Detect
## Overview
This skill covers detection of tamper security incidents and anomalies on Linux systems. Detect utmp/wtmp login record tampering — identify modifications to /var/run/utmp, /var/log/wtmp, /var/log/btmp used to erase attacker login history.
## When to Use
- When investigating or working with tamper in a log integrity and forensics context
- When detecting tamper compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: who, last, lastb, utmpdump, inotifywait /var/log/wtmp
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for logging-utmp-wtmp-tamper-detect
```
## Forensic Workflow
1. Identify scope — determine what tamper elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| tamper indicator | T1070.006 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "logging-utmp-wtmp-tamper-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
