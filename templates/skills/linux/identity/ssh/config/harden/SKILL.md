
---
name: identity-ssh-config-harden
description: Harden SSH server configuration (sshd_config) — disable root login, enforce key-only auth, restrict ciphers, set idle timeout, enable strict mode, and validate config.
domain: cybersecurity
subdomain: identity-hardening
tags:
- linux
- ssh
- sshd
- harden
- configuration
nist_csf:
- PR.IP-01
- PR.PT-01
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1021.004
- T1078
capec: []
---
# Identity Ssh Config Harden
## Overview
This skill applies security hardening controls to config on Linux. Harden SSH server configuration (sshd_config) — disable root login, enforce key-only auth, restrict ciphers, set idle timeout, enable strict mode, and validate config.
## When to Use
- When investigating or working with config in a Linux identity and authentication security context
- When applying security controls to config
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: /etc/ssh/sshd_config, ssh-audit, sshd -t
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for identity-ssh-config-harden
```
## Forensic Workflow
1. Identify scope — determine what config elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| config indicator | T1021.004 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "identity-ssh-config-harden" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
