---
name: detecting-api-enumeration-attacks
description: "Detect and prevent API enumeration attacks including BOLA and IDOR exploitation by monitoring sequential identifier"
domain: cybersecurity
subdomain: api-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-api-enumeration-attacks/SKILL.md"
---
# Detecting Api Enumeration Attacks

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-api-enumeration-attacks/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-api-enumeration-attacks", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-api-enumeration-attacks")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
