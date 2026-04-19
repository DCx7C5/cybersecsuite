
---
name: hardening-aslr-nx-configure-verify
description: Verify and configure ASLR and NX/DEP stack protection — check randomization level, verify NX bit on stack/heap, audit execstack binaries, and configure system-wide settings.
domain: cybersecurity
subdomain: hardening-assessment
tags:
- linux
- aslr
- nx
- dep
- harden
- verify
nist_csf:
- PR.DS-06
- ID.RA-05
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []
---
# Hardening Aslr Nx Configure Verify
## Overview
This skill verifies the integrity and authenticity of configure. Verify and configure ASLR and NX/DEP stack protection — check randomization level, verify NX bit on stack/heap, audit execstack binaries, and configure system-wide settings.
## When to Use
- When investigating or working with configure in a system hardening assessment context
- When verifying integrity of configure
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: checksec, /proc/sys/kernel/randomize_va_space, execstack, paxtest
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for hardening-aslr-nx-configure-verify
```
## Forensic Workflow
1. Identify scope — determine what configure elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| configure indicator | T1068 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "hardening-aslr-nx-configure-verify" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
