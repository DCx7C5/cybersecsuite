
---
name: hardening-selinux-policy-audit
description: Audit SELinux policy effectiveness — review policy modules, identify permissive domains, audit-allow rules, and detect policy weaknesses that allow privilege escalation.
domain: cybersecurity
subdomain: hardening-assessment
tags:
- linux
- selinux
- policy
- audit
- mac
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
- T1548
capec: []
---
# Hardening Selinux Policy Audit
## Overview
This skill audits policy configuration and security posture on Linux systems. Audit SELinux policy effectiveness — review policy modules, identify permissive domains, audit-allow rules, and detect policy weaknesses that allow privilege escalation.
## When to Use
- When investigating or working with policy in a system hardening assessment context
- When reviewing policy configuration against security standards
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: seinfo, sesearch, audit2allow, semodule -l, /var/log/audit
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for hardening-selinux-policy-audit
```
## Forensic Workflow
1. Identify scope — determine what policy elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| policy indicator | T1068 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "hardening-selinux-policy-audit" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
