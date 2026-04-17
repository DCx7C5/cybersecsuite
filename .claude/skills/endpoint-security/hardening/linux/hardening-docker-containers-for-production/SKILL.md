---
name: hardening-docker-containers-for-production
description: "Hardening Docker containers for production involves applying security best practices aligned with CIS Docker"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hardening-docker-containers-for-production/SKILL.md"
---
# Hardening Docker Containers For Production

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hardening-docker-containers-for-production/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="hardening-docker-containers-for-production", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="hardening-docker-containers-for-production")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
