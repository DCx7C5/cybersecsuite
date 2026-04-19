
---
name: identity-shadow-file-tamper-detect
description: Detect /etc/shadow and /etc/passwd tampering — identify unauthorized modifications to credential stores, added backdoor accounts, and hash algorithm downgrades.
domain: cybersecurity
subdomain: identity-forensics
tags:
- linux
- shadow
- passwd
- tamper
- backdoor
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1003.008
- T1136.001
capec: []
---
# Identity Shadow File Tamper Detect
## Overview
This skill covers detection of tamper security incidents and anomalies on Linux systems. Detect /etc/shadow and /etc/passwd tampering — identify unauthorized modifications to credential stores, added backdoor accounts, and hash algorithm downgrades.
## When to Use
- When investigating or working with tamper in a Linux identity and authentication security context
- When detecting tamper compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: inotifywait /etc/shadow, aide, debsums, auditd
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for identity-shadow-file-tamper-detect
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
| tamper indicator | T1003.008 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "identity-shadow-file-tamper-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
