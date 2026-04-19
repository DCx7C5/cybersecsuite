
---
name: forensics-timeline-plaso-create
description: Create a forensic super-timeline of a Linux system using Plaso (log2timeline) — aggregate artifacts from filesystem, logs, shell history, browser data into a unified timeline.
domain: cybersecurity
subdomain: forensic-analysis
tags:
- linux
- plaso
- log2timeline
- timeline
- forensics
nist_csf:
- ID.RA-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1005
- T1070
capec: []
---
# Forensics Timeline Plaso Create
## Overview
Create a forensic super-timeline of a Linux system using Plaso (log2timeline) — aggregate artifacts from filesystem, logs, shell history, browser data into a unified timeline.
## When to Use
- When investigating or working with plaso in a Linux forensic investigation context
- When working with plaso in security context
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: log2timeline.py, psort.py, pinfo.py, /var/log, ~/.bash_history
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for forensics-timeline-plaso-create
```
## Forensic Workflow
1. Identify scope — determine what plaso elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| plaso indicator | T1005 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "forensics-timeline-plaso-create" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
