---
name: testing-jwt-token-security
description: "Assessing JSON Web Token implementations for cryptographic weaknesses, algorithm confusion attacks, and authorization"
domain: cybersecurity
subdomain: web-application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-jwt-token-security/SKILL.md"
---
# Testing Jwt Token Security

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/testing-jwt-token-security/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="testing-jwt-token-security", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="testing-jwt-token-security")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
