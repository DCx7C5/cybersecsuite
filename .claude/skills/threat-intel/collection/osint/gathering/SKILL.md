---
name: performing-open-source-intelligence-gathering
description: "Open Source Intelligence (OSINT) gathering is the first active phase of a red team engagement, where operators"
domain: cybersecurity
subdomain: red-teaming
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-open-source-intelligence-gathering/SKILL.md"
---
# Performing Open Source Intelligence Gathering

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-open-source-intelligence-gathering/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-open-source-intelligence-gathering", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-open-source-intelligence-gathering")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@red-teaming-analyst` or `@cybersec-agent`
