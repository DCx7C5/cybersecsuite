
---
name: hardware-thunderbolt-dma-attack-detect
description: Detect Thunderbolt DMA attack vectors (Thunderspy) — enumerate Thunderbolt devices, check security levels, and detect unauthorized DMA access to host memory.
domain: cybersecurity
subdomain: hardware-security
tags:
- linux
- thunderbolt
- dma
- thunderspy
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1200
capec: []
---
# Hardware Thunderbolt Dma Attack Detect
## Overview
This skill covers detection of attack security incidents and anomalies on Linux systems. Detect Thunderbolt DMA attack vectors (Thunderspy) — enumerate Thunderbolt devices, check security levels, and detect unauthorized DMA access to host memory.
## When to Use
- When investigating or working with attack in a hardware and firmware security context
- When detecting attack compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: thunderspy tools, /sys/bus/thunderbolt, boltctl
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for hardware-thunderbolt-dma-attack-detect
```
## Forensic Workflow
1. Identify scope — determine what attack elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| attack indicator | T1200 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "hardware-thunderbolt-dma-attack-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
