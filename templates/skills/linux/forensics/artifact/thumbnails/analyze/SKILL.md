
---
name: forensics-artifact-thumbnails-analyze
description: Analyze thumbnail cache artifacts for forensic investigation — extract GNOME/KDE thumbnail databases to recover deleted image evidence and reconstruct accessed file history.
domain: cybersecurity
subdomain: forensic-analysis
tags:
- linux
- thumbnails
- cache
- artifact
- forensics
nist_csf:
- DE.AE-02
- RS.AN-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1005
capec: []
---
# Forensics Artifact Thumbnails Analyze
## Overview
This skill provides deep technical analysis capabilities for thumbnails on Linux. Analyze thumbnail cache artifacts for forensic investigation — extract GNOME/KDE thumbnail databases to recover deleted image evidence and reconstruct accessed file history.
## When to Use
- When investigating or working with thumbnails in a Linux forensic investigation context
- When performing deep technical analysis of thumbnails
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: ~/.cache/thumbnails/, file, exiftool, sqlite3
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for forensics-artifact-thumbnails-analyze
```
## Forensic Workflow
1. Identify scope — determine what thumbnails elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| thumbnails indicator | T1005 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "forensics-artifact-thumbnails-analyze" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
