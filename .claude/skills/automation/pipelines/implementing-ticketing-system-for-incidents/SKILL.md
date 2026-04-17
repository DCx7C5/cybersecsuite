---
name: implementing-ticketing-system-for-incidents
description: "'Implements an integrated incident ticketing system connecting SIEM alerts to ServiceNow, Jira, or TheHive for"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-ticketing-system-for-incidents/SKILL.md"
---
# Implementing Ticketing System For Incidents

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-ticketing-system-for-incidents/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-ticketing-system-for-incidents", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-ticketing-system-for-incidents")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
