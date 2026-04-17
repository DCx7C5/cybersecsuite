---
name: building-ioc-enrichment-pipeline-with-opencti
description: "OpenCTI is an open-source platform for managing cyber threat intelligence knowledge, built on STIX 2.1 as its"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-ioc-enrichment-pipeline-with-opencti/SKILL.md"
---
# Building Ioc Enrichment Pipeline With Opencti

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-ioc-enrichment-pipeline-with-opencti/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="building-ioc-enrichment-pipeline-with-opencti", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-ioc-enrichment-pipeline-with-opencti")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
