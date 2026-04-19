
---
name: identity-gshadow-group-audit
description: Audit /etc/gshadow and group privilege assignments — identify groups with excessive members, sudo-equivalent groups (wheel, sudo, docker, disk), and shadow group misconfigurations.
domain: cybersecurity
subdomain: identity-security
tags:
- linux
- gshadow
- group
- privilege
- audit
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
# Identity Gshadow Group Audit
## Overview
This skill audits group configuration and security posture on Linux systems. Audit /etc/gshadow and group privilege assignments — identify groups with excessive members, sudo-equivalent groups (wheel, sudo, docker, disk), and shadow group misconfigurations.
## When to Use
- When investigating or working with group in a Linux identity and authentication security context
- When reviewing group configuration against security standards
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /etc/gshadow, /etc/group, getent group, id
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for identity-gshadow-group-audit
```
## Forensic Workflow
1. Identify scope — determine what group elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| group indicator | T1078 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "identity-gshadow-group-audit" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
