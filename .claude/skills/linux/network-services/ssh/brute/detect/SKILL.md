
---
name: network-services-ssh-brute-detect
description: Detect SSH brute force attacks — analyze /var/log/auth.log for failed authentication patterns, configure fail2ban rules, and identify credential stuffing campaigns.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- ssh
- brute-force
- detect
- auth-log
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1110.001
- T1021.004
capec: []
---
# Network Services Ssh Brute Detect
## Overview
This skill covers detection of brute security incidents and anomalies on Linux systems. Detect SSH brute force attacks — analyze /var/log/auth.log for failed authentication patterns, configure fail2ban rules, and identify credential stuffing campaigns.
## When to Use
- When investigating or working with brute in a Linux network service security context
- When detecting brute compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /var/log/auth.log, fail2ban, lastb, journalctl -u ssh
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for network-services-ssh-brute-detect
```
## Forensic Workflow
1. Identify scope — determine what brute elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| brute indicator | T1110.001 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "network-services-ssh-brute-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
