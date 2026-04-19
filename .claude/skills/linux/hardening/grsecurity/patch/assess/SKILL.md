
---
name: hardening-grsecurity-patch-assess
description: Assess Grsecurity/PaX kernel hardening patch effectiveness — evaluate RBAC policy, UDEREF, SMEP/SMAP enforcement, and PAX_MEMORY_SANITIZE configuration.
domain: cybersecurity
subdomain: hardening-assessment
tags:
- linux
- grsecurity
- pax
- kernel
- hardening
nist_csf:
- ID.RA-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []
---
# Hardening Grsecurity Patch Assess
## Overview
Assess Grsecurity/PaX kernel hardening patch effectiveness — evaluate RBAC policy, UDEREF, SMEP/SMAP enforcement, and PAX_MEMORY_SANITIZE configuration.
## When to Use
- When investigating or working with patch in a system hardening assessment context
- When working with patch in security context
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: grsec, paxtest, /proc/sys/kernel/grsecurity/
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for hardening-grsecurity-patch-assess
```
## Forensic Workflow
1. Identify scope — determine what patch elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| patch indicator | T1068 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "hardening-grsecurity-patch-assess" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
