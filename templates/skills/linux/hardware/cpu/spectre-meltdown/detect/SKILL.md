
---
name: hardware-cpu-spectre-meltdown-detect
description: Detect Spectre and Meltdown hardware side-channel vulnerability exposure on Linux systems via microcode version checks, kernel mitigations, and CPU flags.
domain: cybersecurity
subdomain: hardware-security
tags:
- linux
- cpu
- spectre
- meltdown
- side-channel
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1600
capec: []
---
# Hardware Cpu Spectre Meltdown Detect
## Overview
This skill covers detection of spectre-meltdown security incidents and anomalies on Linux systems. Detect Spectre and Meltdown hardware side-channel vulnerability exposure on Linux systems via microcode version checks, kernel mitigations, and CPU flags.
## When to Use
- When investigating or working with spectre-meltdown in a hardware and firmware security context
- When detecting spectre-meltdown compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: cpu flags, /proc/cpuinfo, spectre-meltdown-checker
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for hardware-cpu-spectre-meltdown-detect
```
## Forensic Workflow
1. Identify scope — determine what spectre-meltdown elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| spectre-meltdown indicator | T1600 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "hardware-cpu-spectre-meltdown-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
