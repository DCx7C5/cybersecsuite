
---
name: kernel-modules-blacklist-audit
description: Audit kernel module blacklists — review /etc/modprobe.d/ blacklist entries, identify missing critical blacklists (cramfs, freevxfs, usb-storage), and verify enforcement.
domain: cybersecurity
subdomain: kernel-hardening
tags:
- linux
- kernel-module
- blacklist
- harden
- modprobe
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1014
- T1200
capec: []
---
# Kernel Modules Blacklist Audit
## Overview
This skill audits blacklist configuration and security posture on Linux systems. Audit kernel module blacklists — review /etc/modprobe.d/ blacklist entries, identify missing critical blacklists (cramfs, freevxfs, usb-storage), and verify enforcement.
## When to Use
- When investigating or working with blacklist in a kernel-level security investigation context
- When reviewing blacklist configuration against security standards
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /etc/modprobe.d/, modprobe, lsmod
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-modules-blacklist-audit
```
## Forensic Workflow
1. Identify scope — determine what blacklist elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| blacklist indicator | T1014 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-modules-blacklist-audit" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
