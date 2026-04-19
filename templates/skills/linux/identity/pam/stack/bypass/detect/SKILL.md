
---
name: identity-pam-stack-bypass-detect
description: Detect PAM authentication stack bypass — identify pam_permit abuse, 'sufficient' control flag manipulation, and PAM stack modifications that bypass authentication.
domain: cybersecurity
subdomain: identity-security
tags:
- linux
- pam
- authentication
- bypass
- detect
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1556.003
- T1078
capec: []
---
# Identity Pam Stack Bypass Detect
## Overview
This skill covers detection of bypass security incidents and anomalies on Linux systems. Detect PAM authentication stack bypass — identify pam_permit abuse, 'sufficient' control flag manipulation, and PAM stack modifications that bypass authentication.
## When to Use
- When investigating or working with bypass in a Linux identity and authentication security context
- When detecting bypass compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /etc/pam.d/, auditd pam events, last, /var/log/auth.log
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for identity-pam-stack-bypass-detect
```
## Forensic Workflow
1. Identify scope — determine what bypass elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| bypass indicator | T1556.003 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "identity-pam-stack-bypass-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
