
---
name: filesystem-inotify-evasion-detect
description: Detect inotify watch evasion — identify techniques to bypass filesystem monitoring (rename tricks, O_CREAT patterns, FIFO bypass) used by malware to avoid detection.
domain: cybersecurity
subdomain: filesystem-security
tags:
- linux
- inotify
- evasion
- bypass
- monitoring
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1562
- T1036
capec: []
---
# Filesystem Inotify Evasion Detect
## Overview
This skill covers detection of evasion security incidents and anomalies on Linux systems. Detect inotify watch evasion — identify techniques to bypass filesystem monitoring (rename tricks, O_CREAT patterns, FIFO bypass) used by malware to avoid detection.
## When to Use
- When investigating or working with evasion in a filesystem forensics context
- When detecting evasion compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: inotifywait, auditd, fanotify, /proc/sys/fs/inotify
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for filesystem-inotify-evasion-detect
```
## Forensic Workflow
1. Identify scope — determine what evasion elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| evasion indicator | T1562 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "filesystem-inotify-evasion-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
