---
name: detecting-service-account-abuse
description: "Detect abuse of service accounts through anomalous interactive logons, privilege escalation, lateral movement,"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-service-account-abuse/SKILL.md"
---
# Detecting Service Account Abuse

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-service-account-abuse/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-service-account-abuse", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-service-account-abuse")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
