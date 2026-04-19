
---
name: containers-apparmor-profile-audit
description: Audit container AppArmor profiles — verify AppArmor confinement for container processes, identify containers with unconfined profiles, and audit policy effectiveness.
domain: cybersecurity
subdomain: container-security
tags:
- linux
- container
- apparmor
- docker
- kubernetes
- audit
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1611
capec: []
---
# Containers Apparmor Profile Audit
## Overview
This skill audits profile configuration and security posture on Linux systems. Audit container AppArmor profiles — verify AppArmor confinement for container processes, identify containers with unconfined profiles, and audit policy effectiveness.
## When to Use
- When investigating or working with profile in a container security context
- When reviewing profile configuration against security standards
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: docker inspect --apparmor, aa-status, /etc/apparmor.d/
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for containers-apparmor-profile-audit
```
## Forensic Workflow
1. Identify scope — determine what profile elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| profile indicator | T1611 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "containers-apparmor-profile-audit" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
