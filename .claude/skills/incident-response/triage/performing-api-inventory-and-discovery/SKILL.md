---
name: performing-api-inventory-and-discovery
description: "'Performs API inventory and discovery to identify all API endpoints in an organization''s environment including"
domain: cybersecurity
subdomain: api-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-api-inventory-and-discovery/SKILL.md"
---
# Performing Api Inventory And Discovery

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-api-inventory-and-discovery/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-api-inventory-and-discovery", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-api-inventory-and-discovery")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
