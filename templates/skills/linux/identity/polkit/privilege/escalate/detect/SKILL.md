
---
name: identity-polkit-privilege-escalate-detect
description: Detect polkit privilege escalation (PwnKit CVE-2021-4034, CVE-2021-3560) — identify pkexec abuse, unauthorized polkit policy modifications, and privilege escalation via D-Bus.
domain: cybersecurity
subdomain: identity-security
tags:
- linux
- polkit
- pkexec
- privesc
- cve
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
- T1548
capec: []
---
# Identity Polkit Privilege Escalate Detect
## Overview
This skill covers detection of escalate security incidents and anomalies on Linux systems. Detect polkit privilege escalation (PwnKit CVE-2021-4034, CVE-2021-3560) — identify pkexec abuse, unauthorized polkit policy modifications, and privilege escalation via D-Bus.
## When to Use
- When investigating or working with escalate in a Linux identity and authentication security context
- When detecting escalate compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: pkexec, polkit version check, auditd, /usr/share/polkit-1/actions
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for identity-polkit-privilege-escalate-detect
```
## Forensic Workflow
1. Identify scope — determine what escalate elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| escalate indicator | T1068 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "identity-polkit-privilege-escalate-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
