
---
name: kernel-memory-slab-corruption-detect
description: Detect kernel slab heap corruption — identify heap spray attempts, use-after-free patterns in kernel allocators (SLUB/SLAB/SLOB), and kernel oops artifacts.
domain: cybersecurity
subdomain: kernel-forensics
tags:
- linux
- slab
- heap
- kernel
- corruption
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
# Kernel Memory Slab Corruption Detect
## Overview
This skill covers detection of corruption security incidents and anomalies on Linux systems. Detect kernel slab heap corruption — identify heap spray attempts, use-after-free patterns in kernel allocators (SLUB/SLAB/SLOB), and kernel oops artifacts.
## When to Use
- When investigating or working with corruption in a kernel-level security investigation context
- When detecting corruption compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /proc/slabinfo, KASAN logs, dmesg, crash tool
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-memory-slab-corruption-detect
```
## Forensic Workflow
1. Identify scope — determine what corruption elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| corruption indicator | T1068 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-memory-slab-corruption-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
