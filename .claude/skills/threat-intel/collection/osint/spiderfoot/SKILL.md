---
name: performing-osint-with-spiderfoot
description: "Automate OSINT collection using SpiderFoot REST API and CLI for target profiling, module-based reconnaissance,"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-osint-with-spiderfoot/SKILL.md"
---
# Performing Osint With Spiderfoot

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-osint-with-spiderfoot/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-osint-with-spiderfoot", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-osint-with-spiderfoot")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@threat-intelligence-analyst` or `@cybersec-agent`
