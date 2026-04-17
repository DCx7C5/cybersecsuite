---
name: implementing-api-gateway-security-controls
description: "'Implements security controls at the API gateway layer including authentication enforcement, rate limiting, request"
domain: cybersecurity
subdomain: api-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-api-gateway-security-controls/SKILL.md"
---
# Implementing Api Gateway Security Controls

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-api-gateway-security-controls/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-api-gateway-security-controls", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-api-gateway-security-controls")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
