
---
name: containers-cgroups-v1-release-agent-detect
description: Detect cgroups v1 container escape via release_agent (CVE-2022-0492) — identify writable release_agent files, notify_on_release abuse, and container escape prerequisites.
domain: cybersecurity
subdomain: container-security
tags:
- linux
- cgroups
- container-escape
- release-agent
- cve
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1611
capec: []
---
# Containers Cgroups V1 Release Agent Detect
## Overview
This skill covers detection of release-agent security incidents and anomalies on Linux systems. Detect cgroups v1 container escape via release_agent (CVE-2022-0492) — identify writable release_agent files, notify_on_release abuse, and container escape prerequisites.
## When to Use
- When investigating or working with release-agent in a container security context
- When detecting release-agent compromise or misuse indicators
- When SOC analysts need structured procedures for this analysis type
## Prerequisites
- Access to a Linux system with appropriate permissions
- Required tools: find /sys/fs/cgroup -name release_agent, mount | grep cgroup
- Appropriate authorization for any testing activities
## Core Commands
```bash
# TODO: Add specific commands for containers-cgroups-v1-release-agent-detect
```
## Forensic Workflow
1. Identify scope — determine what release-agent elements are in scope
2. Collect baseline — gather current state before changes
3. Analyze — apply relevant commands and tools
4. Document — record findings with timestamps and hashes
5. Report — correlate with MITRE ATT&CK techniques
## MITRE ATT&CK Mapping
| Finding | Technique |
|---------|-----------|
| release-agent indicator | T1611 |
## CyberSecSuite Integration
```bash
mcp__cybersec__case_open --title "containers-cgroups-v1-release-agent-detect" --type investigation
mcp__cybersec__add_finding --title "..." --severity medium --description "..."
mcp__cybersec__add_ioc --type host --value "..." --confidence 0.8
mcp__cybersec__suggest_mitre --description "..."
```
**Agent:** `@cybersec-agent` → delegates to appropriate specialist
