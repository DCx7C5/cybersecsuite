
---
name: processes-elf-section-inject-detect
description: Detect ELF binary section injection — identify extra sections added to system binaries, unusual section names, and section-based persistence in modified executables.
domain: cybersecurity
subdomain: process-forensics
tags:
- linux
- elf
- section
- injection
- binary
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1036
- T1195
capec: []
---
# Processes Elf Section Inject Detect
## Overview
This skill covers detection of inject security incidents and anomalies on Linux systems. Detect ELF binary section injection — identify extra sections added to system binaries, unusual section names, and section-based persistence in modified executables.
## When to Use
- When investigating or working with inject in a process memory and execution forensics context
- When detecting inject compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: readelf -S, objdump, debsums, rpm -V
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for processes-elf-section-inject-detect
```
## Forensic Workflow
1. Identify scope — determine what inject elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| inject indicator | T1036 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "processes-elf-section-inject-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
