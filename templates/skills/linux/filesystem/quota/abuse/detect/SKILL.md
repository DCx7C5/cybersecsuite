
---
name: filesystem-quota-abuse-detect
description: Detect disk quota abuse — identify quota bypass techniques, soft/hard limit manipulation, and quota exhaustion attacks used for denial of service.
domain: cybersecurity
subdomain: filesystem-security
tags:
- linux
- quota
- disk
- abuse
- dos
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1499
capec: []
---
# Filesystem Quota Abuse Detect
## Overview
This skill covers detection of abuse security incidents and anomalies on Linux systems. Detect disk quota abuse — identify quota bypass techniques, soft/hard limit manipulation, and quota exhaustion attacks used for denial of service.
## When to Use
- When investigating or working with abuse in a filesystem forensics context
- When detecting abuse compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: quota, repquota, edquota, /proc/fs/quota
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for filesystem-quota-abuse-detect
```
## Forensic Workflow
1. Identify scope — determine what abuse elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| abuse indicator | T1499 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "filesystem-quota-abuse-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
