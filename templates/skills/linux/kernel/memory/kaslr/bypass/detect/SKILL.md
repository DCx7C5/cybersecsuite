
---
name: kernel-memory-kaslr-bypass-detect
description: Detect KASLR (Kernel Address Space Layout Randomization) bypass attempts — side-channel leaks via /proc/kallsyms, timing attacks, and information disclosure vulnerabilities.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- kaslr
- kernel
- aslr
- bypass
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
# Kernel Memory Kaslr Bypass Detect
## Overview
This skill covers detection of bypass security incidents and anomalies on Linux systems. Detect KASLR (Kernel Address Space Layout Randomization) bypass attempts — side-channel leaks via /proc/kallsyms, timing attacks, and information disclosure vulnerabilities.
## When to Use
- When investigating or working with bypass in a kernel-level security investigation context
- When detecting bypass compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /proc/kallsyms, dmesg, sysctl kernel.kptr_restrict
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-memory-kaslr-bypass-detect
```
## Forensic Workflow
1. Identify scope — determine what bypass elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| bypass indicator | T1068 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-memory-kaslr-bypass-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
