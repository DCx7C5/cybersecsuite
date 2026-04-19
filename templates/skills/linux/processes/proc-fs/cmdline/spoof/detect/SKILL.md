
---
name: processes-proc-fs-cmdline-spoof-detect
description: Detect process name and cmdline spoofing — identify processes manipulating argv[0], prctl(PR_SET_NAME), or /proc/self/comm to disguise malicious activity.
domain: cybersecurity
subdomain: process-forensics
tags:
- linux
- proc
- cmdline
- spoof
- masquerade
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1036.005
capec: []
---
# Processes Proc Fs Cmdline Spoof Detect
## Overview
This skill covers detection of spoof security incidents and anomalies on Linux systems. Detect process name and cmdline spoofing — identify processes manipulating argv[0], prctl(PR_SET_NAME), or /proc/self/comm to disguise malicious activity.
## When to Use
- When investigating or working with spoof in a process memory and execution forensics context
- When detecting spoof compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /proc/*/cmdline, /proc/*/comm, auditd exec
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for processes-proc-fs-cmdline-spoof-detect
```
## Forensic Workflow
1. Identify scope — determine what spoof elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| spoof indicator | T1036.005 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "processes-proc-fs-cmdline-spoof-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
