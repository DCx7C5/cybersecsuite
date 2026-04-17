---
name: performing-indicator-lifecycle-management
description: "Indicator lifecycle management tracks IOCs from initial discovery through validation, enrichment, deployment,"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-indicator-lifecycle-management/SKILL.md"
---
# Performing Indicator Lifecycle Management

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-indicator-lifecycle-management/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-indicator-lifecycle-management", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-indicator-lifecycle-management")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@threat-intelligence-analyst` or `@cybersec-agent`
