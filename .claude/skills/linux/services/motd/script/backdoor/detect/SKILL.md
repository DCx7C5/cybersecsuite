
---
name: services-motd-script-backdoor-detect
description: Detect /etc/update-motd.d/ script backdoors — identify unauthorized executable scripts in MOTD directories that execute as root on every SSH login for persistence or C2.
domain: cybersecurity
subdomain: persistence-detection
tags:
- linux
- motd
- update-motd
- backdoor
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1037
- T1543
capec: []
---
# Services Motd Script Backdoor Detect
## Overview
This skill covers detection of backdoor security incidents and anomalies on Linux systems. Detect /etc/update-motd.d/ script backdoors — identify unauthorized executable scripts in MOTD directories that execute as root on every SSH login for persistence or C2.
## When to Use
- When investigating or working with backdoor in a service and persistence investigation context
- When detecting backdoor compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /etc/update-motd.d/, /etc/motd, ls -la, sha256sum
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for services-motd-script-backdoor-detect
```
## Forensic Workflow
1. Identify scope — determine what backdoor elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| backdoor indicator | T1037 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "services-motd-script-backdoor-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
