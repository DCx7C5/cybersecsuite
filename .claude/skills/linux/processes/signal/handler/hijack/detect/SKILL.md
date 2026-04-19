
---
name: processes-signal-handler-hijack-detect
description: Detect signal handler hijacking — identify processes registering unusual signal handlers (SIGSEGV, SIGILL) to gain code execution or persist through crashes.
domain: cybersecurity
subdomain: process-forensics
tags:
- linux
- signal
- handler
- hijack
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1055
- T1543
capec: []
---
# Processes Signal Handler Hijack Detect
## Overview
This skill covers detection of hijack security incidents and anomalies on Linux systems. Detect signal handler hijacking — identify processes registering unusual signal handlers (SIGSEGV, SIGILL) to gain code execution or persist through crashes.
## When to Use
- When investigating or working with hijack in a process memory and execution forensics context
- When detecting hijack compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: gdb info signals, /proc/*/status, auditd sigaction
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for processes-signal-handler-hijack-detect
```
## Forensic Workflow
1. Identify scope — determine what hijack elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| hijack indicator | T1055 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "processes-signal-handler-hijack-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
