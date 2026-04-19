
---
name: hardening-kernel-config-audit
description: Audit kernel build configuration for security settings — review /boot/config-*, check for missing hardening options (CFI, SMEP, SMAP, KASLR, KPTI) against security benchmarks.
domain: cybersecurity
subdomain: hardening-assessment
tags:
- linux
- kernel
- config
- audit
- harden
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
- T1600
capec: []
---
# Hardening Kernel Config Audit
## Overview
This skill audits config configuration and security posture on Linux systems. Audit kernel build configuration for security settings — review /boot/config-*, check for missing hardening options (CFI, SMEP, SMAP, KASLR, KPTI) against security benchmarks.
## When to Use
- When investigating or working with config in a system hardening assessment context
- When reviewing config configuration against security standards
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /boot/config-$(uname -r), kconfig-hardened-check
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for hardening-kernel-config-audit
```
## Forensic Workflow
1. Identify scope — determine what config elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| config indicator | T1068 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "hardening-kernel-config-audit" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
