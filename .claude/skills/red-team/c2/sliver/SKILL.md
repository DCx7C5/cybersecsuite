---
name: building-c2-infrastructure-with-sliver-framework
description: "Build and configure a resilient command-and-control infrastructure using BishopFox's Sliver C2 framework with"
domain: cybersecurity
subdomain: red-teaming
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-c2-infrastructure-with-sliver-framework/SKILL.md"
---
# Building C2 Infrastructure With Sliver Framework

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-c2-infrastructure-with-sliver-framework/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="building-c2-infrastructure-with-sliver-framework", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-c2-infrastructure-with-sliver-framework")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@red-teaming-analyst` or `@cybersec-agent`
