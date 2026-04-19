
---
name: forensics-artifact-bash-history-collect
description: Collect and preserve shell history artifacts for forensic investigation — acquire .bash_history, .zsh_history, and in-memory history from all users including cleared history artifacts.
domain: cybersecurity
subdomain: forensic-collection
tags:
- linux
- bash
- history
- artifact
- forensics
nist_csf:
- RS.AN-01
- DE.CM-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1070.003
- T1005
capec: []
---
# Forensics Artifact Bash History Collect
## Overview
This skill covers collection and preservation of bash-history artifacts for forensic investigation. Collect and preserve shell history artifacts for forensic investigation — acquire .bash_history, .zsh_history, and in-memory history from all users including cleared history artifacts.
## When to Use
- When investigating or working with bash-history in a Linux forensic investigation context
- When collecting forensic artifacts from bash-history
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: find /home /root -name '.*history', strings /proc/*/mem | grep HIST
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for forensics-artifact-bash-history-collect
```
## Forensic Workflow
1. Identify scope — determine what bash-history elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| bash-history indicator | T1070.003 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "forensics-artifact-bash-history-collect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
