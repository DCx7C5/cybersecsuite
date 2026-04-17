---
name: performing-http-parameter-pollution-attack
description: "Execute HTTP Parameter Pollution attacks to bypass input validation, WAF rules, and security controls by injecting"
domain: cybersecurity
subdomain: web-application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-http-parameter-pollution-attack/SKILL.md"
---
# Performing Http Parameter Pollution Attack

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-http-parameter-pollution-attack/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-http-parameter-pollution-attack", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-http-parameter-pollution-attack")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
