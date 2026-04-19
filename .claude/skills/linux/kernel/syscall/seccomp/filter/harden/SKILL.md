
---
name: kernel-syscall-seccomp-filter-harden
description: Apply and audit seccomp-BPF filters to restrict syscall surface — create minimal syscall allowlists, verify filter inheritance, and test filter effectiveness.
domain: cybersecurity
subdomain: kernel-hardening
tags:
- linux
- seccomp
- syscall
- sandbox
- harden
nist_csf:
- PR.IP-01
- PR.PT-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []
---
# Kernel Syscall Seccomp Filter Harden
## Overview
This skill applies security hardening controls to filter on Linux. Apply and audit seccomp-BPF filters to restrict syscall surface — create minimal syscall allowlists, verify filter inheritance, and test filter effectiveness.
## When to Use
- When investigating or working with filter in a kernel-level security investigation context
- When applying security controls to filter
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: seccomp-tools, libseccomp, auditd
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-syscall-seccomp-filter-harden
```
## Forensic Workflow
1. Identify scope — determine what filter elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| filter indicator | T1068 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-syscall-seccomp-filter-harden" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
