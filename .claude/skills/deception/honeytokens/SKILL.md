---
name: deploying-honeypots-for-threat-intelligence
description: ""
domain: cybersecurity
subdomain: 
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: []
tags: []
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-honeypots-for-threat-intelligence/SKILL.md"
---
# Deploying Honeypots For Threat Intelligence

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-honeypots-for-threat-intelligence/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="deploying-honeypots-for-threat-intelligence", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="deploying-honeypots-for-threat-intelligence")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@cybersecurity-analyst` or `@cybersec-agent`
