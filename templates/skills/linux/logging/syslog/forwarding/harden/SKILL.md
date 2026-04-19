
---
name: logging-syslog-forwarding-harden
description: Harden syslog forwarding configuration — configure TLS-encrypted log forwarding (rsyslog/syslog-ng), prevent log injection, and set up centralized SIEM integration securely.
domain: cybersecurity
subdomain: logging-hardening
tags:
- linux
- syslog
- rsyslog
- forwarding
- harden
- tls
nist_csf:
- PR.IP-01
- PR.PT-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1562.001
capec: []
---
# Logging Syslog Forwarding Harden
## Overview
This skill applies security hardening controls to forwarding on Linux. Harden syslog forwarding configuration — configure TLS-encrypted log forwarding (rsyslog/syslog-ng), prevent log injection, and set up centralized SIEM integration securely.
## When to Use
- When investigating or working with forwarding in a log integrity and forensics context
- When applying security controls to forwarding
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /etc/rsyslog.conf, rsyslog TLS, syslog-ng, journald forward
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for logging-syslog-forwarding-harden
```
## Forensic Workflow
1. Identify scope — determine what forwarding elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| forwarding indicator | T1562.001 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "logging-syslog-forwarding-harden" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
