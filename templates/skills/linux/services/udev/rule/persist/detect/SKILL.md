
---
name: services-udev-rule-persist-detect
description: Detect udev rule persistence — inspect /etc/udev/rules.d/ and /lib/udev/rules.d/ for unauthorized rules that execute commands on device events, commonly used for persistence.
domain: cybersecurity
subdomain: persistence-detection
tags:
- linux
- udev
- rule
- persistence
- device
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1543
- T1037
capec: []
---
# Services Udev Rule Persist Detect
## Overview
This skill covers detection of persist security incidents and anomalies on Linux systems. Detect udev rule persistence — inspect /etc/udev/rules.d/ and /lib/udev/rules.d/ for unauthorized rules that execute commands on device events, commonly used for persistence.
## When to Use
- When investigating or working with persist in a service and persistence investigation context
- When detecting persist compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /etc/udev/rules.d/, udevadm monitor, sha256sum rules
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for services-udev-rule-persist-detect
```
## Forensic Workflow
1. Identify scope — determine what persist elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| persist indicator | T1543 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "services-udev-rule-persist-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
