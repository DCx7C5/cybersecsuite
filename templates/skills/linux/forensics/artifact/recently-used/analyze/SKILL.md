
---
name: forensics-artifact-recently-used-analyze
description: Analyze recently-used file artifacts on Linux — extract GTK recently-used.xbel, KDE recent documents, and XDG runtime artifacts to reconstruct user/attacker file access timeline.
domain: cybersecurity
subdomain: forensic-analysis
tags:
- linux
- recently-used
- xbel
- gtk
- artifact
- timeline
nist_csf:
- DE.AE-02
- RS.AN-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1005
- T1083
capec: []
---
# Forensics Artifact Recently Used Analyze
## Overview
This skill provides deep technical analysis capabilities for recently-used on Linux. Analyze recently-used file artifacts on Linux — extract GTK recently-used.xbel, KDE recent documents, and XDG runtime artifacts to reconstruct user/attacker file access timeline.
## When to Use
- When investigating or working with recently-used in a Linux forensic investigation context
- When performing deep technical analysis of recently-used
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: ~/.local/share/recently-used.xbel, xmllint, strings
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for forensics-artifact-recently-used-analyze
```
## Forensic Workflow
1. Identify scope — determine what recently-used elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| recently-used indicator | T1005 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "forensics-artifact-recently-used-analyze" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
