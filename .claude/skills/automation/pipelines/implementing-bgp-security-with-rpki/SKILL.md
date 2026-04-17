---
name: implementing-bgp-security-with-rpki
description: "Implement BGP route origin validation using RPKI with Route Origin Authorizations, RPKI-to-Router protocol, and"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-bgp-security-with-rpki/SKILL.md"
---
# Implementing Bgp Security With Rpki

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-bgp-security-with-rpki/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-bgp-security-with-rpki", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-bgp-security-with-rpki")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
