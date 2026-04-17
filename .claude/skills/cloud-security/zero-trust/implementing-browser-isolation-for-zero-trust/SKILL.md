---
name: implementing-browser-isolation-for-zero-trust
description: "'Deploys remote browser isolation (RBI) as a core component of a Zero Trust architecture. Implements isolation"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-browser-isolation-for-zero-trust/SKILL.md"
---
# Implementing Browser Isolation For Zero Trust

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-browser-isolation-for-zero-trust/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-browser-isolation-for-zero-trust", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-browser-isolation-for-zero-trust")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
