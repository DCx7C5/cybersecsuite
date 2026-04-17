---
name: analyzing-threat-landscape-with-misp
description: "Analyze the threat landscape using MISP (Malware Information Sharing Platform) by querying event statistics,"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-threat-landscape-with-misp/SKILL.md"
---
# Analyzing Threat Landscape With Misp

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-threat-landscape-with-misp/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-threat-landscape-with-misp", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-threat-landscape-with-misp")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@threat-intelligence-analyst` or `@cybersec-agent`
