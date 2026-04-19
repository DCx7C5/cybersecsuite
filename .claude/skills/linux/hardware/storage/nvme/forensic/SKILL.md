
---
name: hardware-storage-nvme-forensic
description: Forensic acquisition and analysis of NVMe block devices — raw image creation, wear leveling artifact analysis, and deleted data recovery from NVMe SSDs.
domain: cybersecurity
subdomain: hardware-forensics
tags:
- linux
- nvme
- storage
- forensics
- block-device
nist_csf:
- RS.AN-01
- RS.AN-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1005
capec: []
---
# Hardware Storage Nvme Forensic
## Overview
This skill covers forensic investigation of nvme artifacts on Linux. Forensic acquisition and analysis of NVMe block devices — raw image creation, wear leveling artifact analysis, and deleted data recovery from NVMe SSDs.
## When to Use
- When investigating or working with nvme in a hardware and firmware security context
- When conducting post-incident forensic investigation of nvme
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: nvme-cli, dc3dd, ewfacquire, /dev/nvme*
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for hardware-storage-nvme-forensic
```
## Forensic Workflow
1. Identify scope — determine what nvme elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| nvme indicator | T1005 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "hardware-storage-nvme-forensic" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
