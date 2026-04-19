
---
name: shell-profile-backdoor-detect
description: Detect shell profile backdoors — scan .bashrc, .bash_profile, .profile, .zshrc, /etc/profile.d/ for injected commands, reverse shells, and credential harvesting hooks.
domain: cybersecurity
subdomain: persistence-detection
tags:
- linux
- shell
- bashrc
- profile
- backdoor
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1546.004
capec: []
---
# Shell Profile Backdoor Detect
## Overview
This skill covers detection of backdoor security incidents and anomalies on Linux systems. Detect shell profile backdoors — scan .bashrc, .bash_profile, .profile, .zshrc, /etc/profile.d/ for injected commands, reverse shells, and credential harvesting hooks.
## When to Use
- When investigating or working with backdoor in a shell environment security context
- When detecting backdoor compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: find /home -name .bashrc, /etc/profile.d/, sha256sum, grep -E
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for shell-profile-backdoor-detect
```
## Forensic Workflow
1. Identify scope — determine what backdoor elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| backdoor indicator | T1546.004 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "shell-profile-backdoor-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
