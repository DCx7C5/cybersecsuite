
---
name: shell-environment-variable-audit
description: Audit shell environment variables across all running processes — identify sensitive data in environment, dangerous overrides, and variables used for privilege escalation.
domain: cybersecurity
subdomain: process-security
tags:
- linux
- environment
- variable
- audit
- security
nist_csf:
- ID.RA-01
- PR.IP-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1078
- T1548
capec: []
---
# Shell Environment Variable Audit
## Overview
This skill audits variable configuration and security posture on Linux systems. Audit shell environment variables across all running processes — identify sensitive data in environment, dangerous overrides, and variables used for privilege escalation.
## When to Use
- When investigating or working with variable in a shell environment security context
- When reviewing variable configuration against security standards
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /proc/*/environ, strings, printenv, auditd execve
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for shell-environment-variable-audit
```
## Forensic Workflow
1. Identify scope — determine what variable elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| variable indicator | T1078 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "shell-environment-variable-audit" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
