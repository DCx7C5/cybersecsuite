
---
name: logging-auditd-bypass-detect
description: Detect auditd bypass and evasion techniques — identify LD_PRELOAD hooking of audit libraries, auditd process termination, rule flooding, and buffer overflow evasion.
domain: cybersecurity
subdomain: logging-security
tags:
- linux
- auditd
- bypass
- evasion
- detect
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1562.001
- T1070
capec: []
---
# Logging Auditd Bypass Detect
## Overview
This skill covers detection of bypass security incidents and anomalies on Linux systems. Detect auditd bypass and evasion techniques — identify LD_PRELOAD hooking of audit libraries, auditd process termination, rule flooding, and buffer overflow evasion.
## When to Use
- When investigating or working with bypass in a log integrity and forensics context
- When detecting bypass compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: pgrep auditd, auditctl -l, /etc/audit/, dmesg
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for logging-auditd-bypass-detect
```
## Forensic Workflow
1. Identify scope — determine what bypass elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| bypass indicator | T1562.001 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "logging-auditd-bypass-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
