
---
name: kernel-boot-uefi-variable-tamper-detect
description: Detect unauthorized UEFI variable manipulation — monitor EFI variable store for persistence via NVRAM, rogue boot entries, and BootOrder manipulation.
domain: cybersecurity
subdomain: kernel-forensics
tags:
- linux
- uefi
- efi-variable
- nvram
- tamper
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1542.001
capec: []
---
# Kernel Boot Uefi Variable Tamper Detect
## Overview
This skill covers detection of tamper security incidents and anomalies on Linux systems. Detect unauthorized UEFI variable manipulation — monitor EFI variable store for persistence via NVRAM, rogue boot entries, and BootOrder manipulation.
## When to Use
- When investigating or working with tamper in a kernel-level security investigation context
- When detecting tamper compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: efivar, efibootmgr, /sys/firmware/efi/efivars
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-boot-uefi-variable-tamper-detect
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
mcp__cybersec__case_open --title "kernel-boot-uefi-variable-tamper-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
