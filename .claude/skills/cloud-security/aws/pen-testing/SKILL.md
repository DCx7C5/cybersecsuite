---
name: performing-cloud-penetration-testing-with-pacu
description: "'Performing authorized AWS penetration testing using Pacu, the open-source AWS exploitation framework, to enumerate"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-cloud-penetration-testing-with-pacu/SKILL.md"
---
# Performing Cloud Penetration Testing With Pacu

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-cloud-penetration-testing-with-pacu/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-cloud-penetration-testing-with-pacu", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-cloud-penetration-testing-with-pacu")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@cloud-security-analyst` or `@cybersec-agent`
