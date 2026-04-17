---
name: detecting-cloud-threats-with-guardduty
description: "'This skill teaches security teams how to deploy and operationalize Amazon GuardDuty for continuous threat detection"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-cloud-threats-with-guardduty/SKILL.md"
---
# Detecting Cloud Threats With Guardduty

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-cloud-threats-with-guardduty/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="detecting-cloud-threats-with-guardduty", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-cloud-threats-with-guardduty")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@cloud-security-analyst` or `@cybersec-agent`
