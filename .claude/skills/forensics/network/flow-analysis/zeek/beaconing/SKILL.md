---
name: detecting-beaconing-patterns-with-zeek
description: "'Performs statistical analysis of Zeek conn.log connection intervals to detect C2 beaconing patterns. Uses the"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-beaconing-patterns-with-zeek/SKILL.md"
---
# Detecting Beaconing Patterns With Zeek

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-beaconing-patterns-with-zeek/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="detecting-beaconing-patterns-with-zeek", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-beaconing-patterns-with-zeek")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@security-operations-analyst` or `@cybersec-agent`
