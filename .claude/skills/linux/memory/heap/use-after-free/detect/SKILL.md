
---
name: memory-heap-use-after-free-detect
description: Detect heap use-after-free vulnerabilities in userland applications — identify dangling pointer dereferences, double-free conditions, and heap metadata corruption.
domain: cybersecurity
subdomain: memory-security
tags:
- linux
- heap
- use-after-free
- uaf
- memory-corruption
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1068
capec: []
---
# Memory Heap Use After Free Detect
## Overview
This skill covers detection of use-after-free security incidents and anomalies on Linux systems. Detect heap use-after-free vulnerabilities in userland applications — identify dangling pointer dereferences, double-free conditions, and heap metadata corruption.
## When to Use
- When investigating or working with use-after-free in a memory security and exploit analysis context
- When detecting use-after-free compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: AddressSanitizer, Valgrind, heaptrack, /proc/*/smaps
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for memory-heap-use-after-free-detect
```
## Forensic Workflow
1. Identify scope — determine what use-after-free elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| use-after-free indicator | T1068 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "memory-heap-use-after-free-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
