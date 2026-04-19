
---
name: network-services-ssh-tunnel-detect
description: Detect unauthorized SSH tunneling — identify LocalForward/RemoteForward/DynamicForward connections, SOCKS proxy via SSH, and SSH as a covert C2 channel.
domain: cybersecurity
subdomain: network-security
tags:
- linux
- ssh
- tunnel
- forward
- c2
- detect
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1572
- T1021.004
capec: []
---
# Network Services Ssh Tunnel Detect
## Overview
This skill covers detection of tunnel security incidents and anomalies on Linux systems. Detect unauthorized SSH tunneling — identify LocalForward/RemoteForward/DynamicForward connections, SOCKS proxy via SSH, and SSH as a covert C2 channel.
## When to Use
- When investigating or working with tunnel in a Linux network service security context
- When detecting tunnel compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: ss -tnp, netstat, sshd_config AllowTcpForwarding, auditd
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for network-services-ssh-tunnel-detect
```
## Forensic Workflow
1. Identify scope — determine what tunnel elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| tunnel indicator | T1572 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "network-services-ssh-tunnel-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
