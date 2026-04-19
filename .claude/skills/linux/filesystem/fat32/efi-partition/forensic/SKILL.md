
---
name: filesystem-fat32-efi-partition-forensic
description: Forensic analysis of the EFI System Partition (ESP) — enumerate ESP contents, detect rogue EFI applications, check bootloader integrity, and identify persistence via ESP.
domain: cybersecurity
subdomain: filesystem-forensics
tags:
- linux
- fat32
- efi
- esp
- bootloader
- forensics
nist_csf:
- RS.AN-01
- RS.AN-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1542.001
capec: []
---
# Filesystem Fat32 Efi Partition Forensic
## Overview
This skill covers forensic investigation of efi-partition artifacts on Linux. Forensic analysis of the EFI System Partition (ESP) — enumerate ESP contents, detect rogue EFI applications, check bootloader integrity, and identify persistence via ESP.
## When to Use
- When investigating or working with efi-partition in a filesystem forensics context
- When conducting post-incident forensic investigation of efi-partition
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: mount /dev/sdX1, efibootmgr, sha256sum, /boot/efi
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for filesystem-fat32-efi-partition-forensic
```
## Forensic Workflow
1. Identify scope — determine what efi-partition elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| efi-partition indicator | T1542.001 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "filesystem-fat32-efi-partition-forensic" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
