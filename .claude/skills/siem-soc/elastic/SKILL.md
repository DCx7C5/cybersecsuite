---
name: performing-threat-hunting-with-elastic-siem
description: "'Performs proactive threat hunting in Elastic Security SIEM using KQL/EQL queries, detection rules, and Timeline"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-threat-hunting-with-elastic-siem/SKILL.md"
---
# Performing Threat Hunting With Elastic Siem

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-threat-hunting-with-elastic-siem/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-threat-hunting-with-elastic-siem", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-threat-hunting-with-elastic-siem")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@soc-operations-analyst` or `@cybersec-agent`
