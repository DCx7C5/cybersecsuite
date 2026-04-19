
---
name: logging-journald-binary-tamper-detect
description: Detect systemd journal log tampering — identify journal file corruption, log rotation abuse, unauthorized journal forwarding, and missing entries indicating attacker log removal.
domain: cybersecurity
subdomain: logging-forensics
tags:
- linux
- journald
- systemd
- log
- tamper
- anti-forensics
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1070.002
capec: []
---
# Logging Journald Binary Tamper Detect
## Overview
This skill covers detection of tamper security incidents and anomalies on Linux systems. Detect systemd journal log tampering — identify journal file corruption, log rotation abuse, unauthorized journal forwarding, and missing entries indicating attacker log removal.
## When to Use
- When investigating or working with tamper in a log integrity and forensics context
- When detecting tamper compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: journalctl --verify, journalctl -u, /var/log/journal/
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for logging-journald-binary-tamper-detect
```
## Forensic Workflow
1. Identify scope — determine what tamper elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| tamper indicator | T1070.002 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "logging-journald-binary-tamper-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
