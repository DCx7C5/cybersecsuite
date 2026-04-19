
---
name: processes-elf-got-hook-detect
description: Detect GOT (Global Offset Table) hooking in ELF binaries — identify runtime function pointer overwrites used by rootkits and malware to intercept shared library calls.
domain: cybersecurity
subdomain: process-forensics
tags:
- linux
- elf
- got
- hook
- rootkit
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1574.007
- T1014
capec: []
---
# Processes Elf Got Hook Detect
## Overview
This skill covers detection of hook security incidents and anomalies on Linux systems. Detect GOT (Global Offset Table) hooking in ELF binaries — identify runtime function pointer overwrites used by rootkits and malware to intercept shared library calls.
## When to Use
- When investigating or working with hook in a process memory and execution forensics context
- When detecting hook compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: readelf -r, objdump -R, /proc/*/maps, pmap
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for processes-elf-got-hook-detect
```
## Forensic Workflow
1. Identify scope — determine what hook elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| hook indicator | T1574.007 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "processes-elf-got-hook-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
