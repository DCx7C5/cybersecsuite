
---
name: network-services-docker-socket-expose-detect
description: Detect exposed Docker daemon socket — identify bind-mounted /var/run/docker.sock in containers (instant root escape), TCP Docker API exposure, and unauthorized socket access.
domain: cybersecurity
subdomain: container-security
tags:
- linux
- docker
- socket
- expose
- root-escape
- detect
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1611
- T1190
capec: []
---
# Network Services Docker Socket Expose Detect
## Overview
This skill covers detection of expose security incidents and anomalies on Linux systems. Detect exposed Docker daemon socket — identify bind-mounted /var/run/docker.sock in containers (instant root escape), TCP Docker API exposure, and unauthorized socket access.
## When to Use
- When investigating or working with expose in a Linux network service security context
- When detecting expose compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: ls -la /var/run/docker.sock, ss -tlnp :2375, docker.service -H
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for network-services-docker-socket-expose-detect
```
## Forensic Workflow
1. Identify scope — determine what expose elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| expose indicator | T1611 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "network-services-docker-socket-expose-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
