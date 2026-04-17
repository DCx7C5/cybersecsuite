---
name: detecting-azure-service-principal-abuse
description: "Detect and investigate Azure service principal abuse including privilege escalation, credential compromise, admin"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-azure-service-principal-abuse/SKILL.md"
---
# Detecting Azure Service Principal Abuse

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-azure-service-principal-abuse/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-azure-service-principal-abuse", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-azure-service-principal-abuse")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
