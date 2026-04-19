
---
name: filesystem-overlayfs-layer-analyze
description: Analyze OverlayFS layers used by container runtimes — inspect upper/lower/work directories, detect file modifications within containers, and recover deleted container artifacts.
domain: cybersecurity
subdomain: filesystem-forensics
tags:
- linux
- overlayfs
- container
- filesystem
- analyze
nist_csf:
- DE.AE-02
- RS.AN-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1005
- T1036
capec: []
---
# Filesystem Overlayfs Layer Analyze
## Overview
This skill provides deep technical analysis capabilities for layer on Linux. Analyze OverlayFS layers used by container runtimes — inspect upper/lower/work directories, detect file modifications within containers, and recover deleted container artifacts.
## When to Use
- When investigating or working with layer in a filesystem forensics context
- When performing deep technical analysis of layer
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /var/lib/docker/overlay2, findmnt, mount
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for filesystem-overlayfs-layer-analyze
```
## Forensic Workflow
1. Identify scope — determine what layer elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| layer indicator | T1005 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "filesystem-overlayfs-layer-analyze" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
