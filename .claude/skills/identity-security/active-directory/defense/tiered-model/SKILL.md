---
name: configuring-active-directory-tiered-model
description: "Implement Microsoft's Enhanced Security Admin Environment (ESAE) tiered administration model for Active Directory."
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-active-directory-tiered-model/SKILL.md"
---
# Configuring Active Directory Tiered Model

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/configuring-active-directory-tiered-model/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="configuring-active-directory-tiered-model", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="configuring-active-directory-tiered-model")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@identity-access-management-analyst` or `@cybersec-agent`
