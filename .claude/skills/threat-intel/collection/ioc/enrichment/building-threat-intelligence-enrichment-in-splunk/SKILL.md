---
name: building-threat-intelligence-enrichment-in-splunk
description: "Build automated threat intelligence enrichment pipelines in Splunk Enterprise Security using lookup tables, modular"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-threat-intelligence-enrichment-in-splunk/SKILL.md"
---
# Building Threat Intelligence Enrichment In Splunk

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-threat-intelligence-enrichment-in-splunk/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="building-threat-intelligence-enrichment-in-splunk", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-threat-intelligence-enrichment-in-splunk")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
