---
name: building-threat-feed-aggregation-with-misp
description: "Deploy MISP (Malware Information Sharing Platform) to aggregate, correlate, and distribute threat intelligence"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-threat-feed-aggregation-with-misp/SKILL.md"
---
# Building Threat Feed Aggregation With Misp

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-threat-feed-aggregation-with-misp/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="building-threat-feed-aggregation-with-misp", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-threat-feed-aggregation-with-misp")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
