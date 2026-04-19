
---
name: kernel-syscall-userfaultfd-race-detect
description: Detect userfaultfd-based race condition exploits — identify processes using userfaultfd to slow kernel operations and win race conditions in privilege escalation.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- userfaultfd
- race-condition
- exploit
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []
---
# Kernel Syscall Userfaultfd Race Detect
## Overview
This skill covers detection of race security incidents and anomalies on Linux systems. Detect userfaultfd-based race condition exploits — identify processes using userfaultfd to slow kernel operations and win race conditions in privilege escalation.
## When to Use
- When investigating or working with race in a kernel-level security investigation context
- When detecting race compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: auditd userfaultfd syscall, /proc/sys/vm/unprivileged_userfaultfd
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-syscall-userfaultfd-race-detect
```
## Forensic Workflow
1. Identify scope — determine what race elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| race indicator | T1068 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-syscall-userfaultfd-race-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
