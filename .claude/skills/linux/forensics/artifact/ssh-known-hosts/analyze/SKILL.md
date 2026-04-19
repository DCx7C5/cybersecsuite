
---
name: forensics-artifact-ssh-known-hosts-analyze
description: Analyze SSH known_hosts files for forensic intelligence — extract host fingerprints, identify lateral movement targets, detect unusual hosts, and correlate with network connections.
domain: cybersecurity
subdomain: forensic-analysis
tags:
- linux
- ssh
- known-hosts
- lateral-movement
- forensics
nist_csf:
- DE.AE-02
- RS.AN-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1021.004
- T1078
capec: []
---
# Forensics Artifact Ssh Known Hosts Analyze
## Overview
This skill provides deep technical analysis capabilities for ssh-known-hosts on Linux. Analyze SSH known_hosts files for forensic intelligence — extract host fingerprints, identify lateral movement targets, detect unusual hosts, and correlate with network connections.
## When to Use
- When investigating or working with ssh-known-hosts in a Linux forensic investigation context
- When performing deep technical analysis of ssh-known-hosts
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: find /home /root -name known_hosts, ssh-keygen -l -f, cat ~/.ssh/known_hosts
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for forensics-artifact-ssh-known-hosts-analyze
```
## Forensic Workflow
1. Identify scope — determine what ssh-known-hosts elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| ssh-known-hosts indicator | T1021.004 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "forensics-artifact-ssh-known-hosts-analyze" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
