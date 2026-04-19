
---
name: processes-proc-fs-mem-inject-detect
description: Detect /proc/pid/mem write injection — identify processes writing to other processes via the /proc filesystem mem file, a stealthy injection technique requiring only ptrace_attach.
domain: cybersecurity
subdomain: process-security
tags:
- linux
- proc
- mem
- injection
- ptrace
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1055
- T1083
capec: []
---
# Processes Proc Fs Mem Inject Detect
## Overview
This skill covers detection of inject security incidents and anomalies on Linux systems. Detect /proc/pid/mem write injection — identify processes writing to other processes via the /proc filesystem mem file, a stealthy injection technique requiring only ptrace_attach.
## When to Use
- When investigating or working with inject in a process memory and execution forensics context
- When detecting inject compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: auditd openat /proc/*/mem, inotifywait, eBPF
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for processes-proc-fs-mem-inject-detect
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
| inject indicator | T1055 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "processes-proc-fs-mem-inject-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
