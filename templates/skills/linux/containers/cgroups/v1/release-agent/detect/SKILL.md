
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
