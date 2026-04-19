
---
name: hardening-sysctl-kernel-harden
description: Harden Linux kernel via sysctl parameters — configure ASLR, kernel pointer hiding, TCP hardening, SYN cookies, ICMP restrictions, and core dump disabling.
domain: cybersecurity
subdomain: hardening-implementation
tags:
- linux
- sysctl
- kernel
- harden
- configuration
nist_csf:
- PR.IP-01
- PR.PT-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
- T1021
capec: []
---
# Hardening Sysctl Kernel Harden
## Overview
This skill applies security hardening controls to kernel on Linux. Harden Linux kernel via sysctl parameters — configure ASLR, kernel pointer hiding, TCP hardening, SYN cookies, ICMP restrictions, and core dump disabling.
## When to Use
- When investigating or working with kernel in a system hardening assessment context
- When applying security controls to kernel
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: sysctl -a, /etc/sysctl.d/, sysctl -p, /proc/sys/kernel
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for hardening-sysctl-kernel-harden
```
## Forensic Workflow
1. Identify scope — determine what kernel elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| kernel indicator | T1068 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "hardening-sysctl-kernel-harden" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
