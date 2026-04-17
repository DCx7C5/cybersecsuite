---
name: performing-log-source-onboarding-in-siem
description: "Perform structured log source onboarding into SIEM platforms by configuring collectors, parsers, normalization,"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-log-source-onboarding-in-siem/SKILL.md"
---
# Performing Log Source Onboarding In Siem

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-log-source-onboarding-in-siem/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-log-source-onboarding-in-siem", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-log-source-onboarding-in-siem")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@soc-operations-analyst` or `@cybersec-agent`
