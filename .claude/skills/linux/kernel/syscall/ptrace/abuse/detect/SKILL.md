
---
name: kernel-syscall-ptrace-abuse-detect
description: Detect ptrace syscall abuse beyond process injection — unauthorized debugger attachment, credential scraping from traced processes, and ptrace-based sandbox escape.
domain: cybersecurity
subdomain: kernel-security
tags:
- linux
- ptrace
- syscall
- abuse
- sandbox-escape
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1055
- T1003
capec: []
---
# Kernel Syscall Ptrace Abuse Detect
## Overview
This skill covers detection of abuse security incidents and anomalies on Linux systems. Detect ptrace syscall abuse beyond process injection — unauthorized debugger attachment, credential scraping from traced processes, and ptrace-based sandbox escape.
## When to Use
- When investigating or working with abuse in a kernel-level security investigation context
- When detecting abuse compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: auditd ptrace, /proc/sys/kernel/yama/ptrace_scope
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for kernel-syscall-ptrace-abuse-detect
```
## Forensic Workflow
1. Identify scope — determine what abuse elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| abuse indicator | T1055 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "kernel-syscall-ptrace-abuse-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
