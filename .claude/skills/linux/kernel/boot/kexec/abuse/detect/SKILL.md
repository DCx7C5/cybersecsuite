
---
name: kernel-boot-kexec-abuse-detect
description: Detect kexec abuse — identify unauthorized kernel replacement via kexec_load syscall, which allows loading a new kernel without hardware reboot (bypasses Secure Boot).
domain: cybersecurity
subdomain: kernel-forensics
tags:
- linux
- kexec
- kernel
- bypass
- secure-boot
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1542
- T1068
capec: []
---
# Kernel Boot Kexec Abuse Detect
## Overview
This skill covers detection of abuse security incidents and anomalies on Linux systems. Detect kexec abuse — identify unauthorized kernel replacement via kexec_load syscall, which allows loading a new kernel without hardware reboot (bypasses Secure Boot).
## When to Use
- When investigating or working with abuse in a kernel-level security investigation context
- When detecting abuse compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: kexec, auditd kexec_load syscall, /proc/sys/kernel/kexec_load_disabled
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-boot-kexec-abuse-detect
```
## Forensic Workflow
1. Identify scope — determine what abuse elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| abuse indicator | T1542 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-boot-kexec-abuse-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
