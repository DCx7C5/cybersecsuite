
---
name: containers-namespace-user-privesc-detect
description: Detect user namespace privilege escalation — identify unprivileged user namespace abuse, newuidmap/newgidmap exploitation, and namespace-based sandbox escape.
domain: cybersecurity
subdomain: container-security
tags:
- linux
- namespace
- user-namespace
- privesc
- container
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1611
- T1068
capec: []
---
# Containers Namespace User Privesc Detect
## Overview
This skill covers detection of privesc security incidents and anomalies on Linux systems. Detect user namespace privilege escalation — identify unprivileged user namespace abuse, newuidmap/newgidmap exploitation, and namespace-based sandbox escape.
## When to Use
- When investigating or working with privesc in a container security context
- When detecting privesc compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /proc/sys/kernel/unprivileged_userns_clone, auditd unshare
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for containers-namespace-user-privesc-detect
```
## Forensic Workflow
1. Identify scope — determine what privesc elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| privesc indicator | T1611 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "containers-namespace-user-privesc-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
