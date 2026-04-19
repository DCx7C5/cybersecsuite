
---
name: hardware-cpu-microcode-integrity-verify
description: Verify CPU microcode integrity and update status to ensure hardware-level mitigations are applied against known CPU vulnerabilities.
domain: cybersecurity
subdomain: hardware-security
tags:
- linux
- cpu
- microcode
- integrity
nist_csf:
- PR.DS-06
- ID.RA-05
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1600
capec: []
---
# Hardware Cpu Microcode Integrity Verify
## Overview
This skill verifies the integrity and authenticity of integrity. Verify CPU microcode integrity and update status to ensure hardware-level mitigations are applied against known CPU vulnerabilities.
## When to Use
- When investigating or working with integrity in a hardware and firmware security context
- When verifying integrity of integrity
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: iucode-tool, cpuid, /sys/devices/system/cpu
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for hardware-cpu-microcode-integrity-verify
```
## Forensic Workflow
1. Identify scope — determine what integrity elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| integrity indicator | T1600 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "hardware-cpu-microcode-integrity-verify" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
