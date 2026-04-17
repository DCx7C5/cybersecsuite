---
name: performing-cloud-asset-inventory-with-cartography
description: "Perform comprehensive cloud asset inventory and relationship mapping using Cartography to build a Neo4j security"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-cloud-asset-inventory-with-cartography/SKILL.md"
---
# Performing Cloud Asset Inventory With Cartography

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-cloud-asset-inventory-with-cartography/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-cloud-asset-inventory-with-cartography", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-cloud-asset-inventory-with-cartography")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
