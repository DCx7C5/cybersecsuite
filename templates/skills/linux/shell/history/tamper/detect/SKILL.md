
---
name: shell-history-tamper-detect
description: Detect shell history tampering — identify HISTFILE=/dev/null tricks, HISTSIZE=0, history deletion, and commands to disable history recording used to cover attacker tracks.
domain: cybersecurity
subdomain: forensic-detection
tags:
- linux
- shell
- history
- tamper
- anti-forensics
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1070.003
capec: []
---
# Shell History Tamper Detect
## Overview
This skill covers detection of tamper security incidents and anomalies on Linux systems. Detect shell history tampering — identify HISTFILE=/dev/null tricks, HISTSIZE=0, history deletion, and commands to disable history recording used to cover attacker tracks.
## When to Use
- When investigating or working with tamper in a shell environment security context
- When detecting tamper compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /home/*/.bash_history, auditd, /proc/*/environ HIST*
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for shell-history-tamper-detect
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
| tamper indicator | T1070.003 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "shell-history-tamper-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
