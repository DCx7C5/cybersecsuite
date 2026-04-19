
---
name: shell-env-ld-library-hijack-detect
description: Detect LD_LIBRARY_PATH and LD_PRELOAD environment variable hijacking — identify environment variable injection that redirects shared library loading to malicious libraries.
domain: cybersecurity
subdomain: process-security
tags:
- linux
- ld-library-path
- ld-preload
- env
- hijack
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1574.006
capec: []
---
# Shell Env Ld Library Hijack Detect
## Overview
This skill covers detection of hijack security incidents and anomalies on Linux systems. Detect LD_LIBRARY_PATH and LD_PRELOAD environment variable hijacking — identify environment variable injection that redirects shared library loading to malicious libraries.
## When to Use
- When investigating or working with hijack in a shell environment security context
- When detecting hijack compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /proc/*/environ, auditd execve, /etc/ld.so.preload
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for shell-env-ld-library-hijack-detect
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
| hijack indicator | T1574.006 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "shell-env-ld-library-hijack-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
