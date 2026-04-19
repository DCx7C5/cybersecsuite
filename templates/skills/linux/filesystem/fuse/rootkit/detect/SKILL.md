
---
name: filesystem-fuse-rootkit-detect
description: Detect FUSE-based filesystem rootkits — identify user-space filesystem mounts that intercept file operations to hide files or manipulate data transparently.
domain: cybersecurity
subdomain: filesystem-forensics
tags:
- linux
- fuse
- rootkit
- filesystem
- hide
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1014
- T1036
capec: []
---
# Filesystem Fuse Rootkit Detect
## Overview
This skill covers detection of rootkit security incidents and anomalies on Linux systems. Detect FUSE-based filesystem rootkits — identify user-space filesystem mounts that intercept file operations to hide files or manipulate data transparently.
## When to Use
- When investigating or working with rootkit in a filesystem forensics context
- When detecting rootkit compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: mount | grep fuse, /proc/mounts, lsof, fusermount
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for filesystem-fuse-rootkit-detect
```
## Forensic Workflow
1. Identify scope — determine what rootkit elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| rootkit indicator | T1014 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "filesystem-fuse-rootkit-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
