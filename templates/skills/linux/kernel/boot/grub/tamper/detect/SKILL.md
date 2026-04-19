
---
name: kernel-boot-grub-tamper-detect
description: Detect GRUB bootloader tampering — check GRUB binary hashes, grub.cfg integrity, password protection, and unauthorized menu entries that could load malicious kernels.
domain: cybersecurity
subdomain: kernel-forensics
tags:
- linux
- grub
- bootloader
- tamper
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1542.001
- T1014
capec: []
---
# Kernel Boot Grub Tamper Detect
## Overview
This skill covers detection of tamper security incidents and anomalies on Linux systems. Detect GRUB bootloader tampering — check GRUB binary hashes, grub.cfg integrity, password protection, and unauthorized menu entries that could load malicious kernels.
## When to Use
- When investigating or working with tamper in a kernel-level security investigation context
- When detecting tamper compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: grub2-install, sha256sum, /boot/grub2/, debsums
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-boot-grub-tamper-detect
```
## Forensic Workflow
1. Identify scope — determine what tamper elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| tamper indicator | T1542.001 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-boot-grub-tamper-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
