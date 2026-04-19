
---
name: filesystem-squashfs-unpack-analyze
description: Unpack and analyze SquashFS images from AppImage, Snap packages, or embedded Linux — extract contents, verify integrity, and scan for malicious payloads.
domain: cybersecurity
subdomain: filesystem-forensics
tags:
- linux
- squashfs
- appimage
- snap
- analyze
nist_csf:
- DE.AE-02
- RS.AN-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1195.002
capec: []
---
# Filesystem Squashfs Unpack Analyze
## Overview
This skill provides deep technical analysis capabilities for unpack on Linux. Unpack and analyze SquashFS images from AppImage, Snap packages, or embedded Linux — extract contents, verify integrity, and scan for malicious payloads.
## When to Use
- When investigating or working with unpack in a filesystem forensics context
- When performing deep technical analysis of unpack
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: unsquashfs, binwalk, file, sha256sum
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for filesystem-squashfs-unpack-analyze
```
## Forensic Workflow
1. Identify scope — determine what unpack elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| unpack indicator | T1195.002 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "filesystem-squashfs-unpack-analyze" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
