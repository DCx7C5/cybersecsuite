
---
name: shell-alias-hijack-detect
description: Detect shell alias hijacking — identify malicious aliases overriding common commands (ls, ps, netstat, sudo) in .bashrc or /etc/profile.d/ used by rootkits to hide activity.
domain: cybersecurity
subdomain: persistence-detection
tags:
- linux
- shell
- alias
- hijack
- rootkit
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1574
- T1036
capec: []
---
# Shell Alias Hijack Detect
## Overview
This skill covers detection of hijack security incidents and anomalies on Linux systems. Detect shell alias hijacking — identify malicious aliases overriding common commands (ls, ps, netstat, sudo) in .bashrc or /etc/profile.d/ used by rootkits to hide activity.
## When to Use
- When investigating or working with hijack in a shell environment security context
- When detecting hijack compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: alias, /home/*/.bashrc, /etc/profile.d/, diff baseline
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for shell-alias-hijack-detect
```
## Forensic Workflow
1. Identify scope — determine what hijack elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| hijack indicator | T1574 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "shell-alias-hijack-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
