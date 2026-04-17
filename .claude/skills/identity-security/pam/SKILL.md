---
name: performing-privileged-account-access-review
description: "Conduct systematic reviews of privileged accounts to validate access rights, identify excessive permissions,"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-privileged-account-access-review/SKILL.md"
---
# Performing Privileged Account Access Review

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-privileged-account-access-review/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-privileged-account-access-review", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-privileged-account-access-review")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@identity-access-management-analyst` or `@cybersec-agent`
