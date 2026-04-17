---
name: correlating-security-events-in-qradar
description: "'Correlates security events in IBM QRadar SIEM using AQL (Ariel Query Language), custom rules, building blocks,"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/correlating-security-events-in-qradar/SKILL.md"
---
# Correlating Security Events In Qradar

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/correlating-security-events-in-qradar/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="correlating-security-events-in-qradar", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="correlating-security-events-in-qradar")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@soc-operations-analyst` or `@cybersec-agent`
