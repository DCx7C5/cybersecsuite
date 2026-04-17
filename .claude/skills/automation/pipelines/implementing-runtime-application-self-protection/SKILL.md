---
name: implementing-runtime-application-self-protection
description: "Deploy Runtime Application Self-Protection (RASP) agents to detect and block attacks from within application"
domain: cybersecurity
subdomain: application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-runtime-application-self-protection/SKILL.md"
---
# Implementing Runtime Application Self Protection

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-runtime-application-self-protection/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-runtime-application-self-protection", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-runtime-application-self-protection")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
