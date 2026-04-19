
---
name: identity-pam-module-backdoor-detect
description: Detect malicious PAM module insertion — identify unauthorized .so files in /lib/security/, modules logging credentials, and modified pam.d configurations.
domain: cybersecurity
subdomain: identity-security
tags:
- linux
- pam
- module
- backdoor
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1556.003
- T1078
capec: []
---
# Identity Pam Module Backdoor Detect
## Overview
This skill covers detection of backdoor security incidents and anomalies on Linux systems. Detect malicious PAM module insertion — identify unauthorized .so files in /lib/security/, modules logging credentials, and modified pam.d configurations.
## When to Use
- When investigating or working with backdoor in a Linux identity and authentication security context
- When detecting backdoor compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /etc/pam.d/, /lib/security/, lsof, sha256sum PAM libs
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for identity-pam-module-backdoor-detect
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
| backdoor indicator | T1556.003 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "identity-pam-module-backdoor-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
