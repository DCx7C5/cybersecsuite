---
name: implementing-next-generation-firewall-with-palo-alto
description: "Configure and deploy Palo Alto Networks next-generation firewalls with App-ID, User-ID, zone-based policies,"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-next-generation-firewall-with-palo-alto/SKILL.md"
---
# Implementing Next Generation Firewall With Palo Alto

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-next-generation-firewall-with-palo-alto/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-next-generation-firewall-with-palo-alto", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-next-generation-firewall-with-palo-alto")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
