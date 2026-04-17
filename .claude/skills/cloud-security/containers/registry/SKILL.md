---
name: securing-container-registry-with-harbor
description: "Harbor is an open-source container registry that provides security features including vulnerability scanning"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/securing-container-registry-with-harbor/SKILL.md"
---
# Securing Container Registry With Harbor

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/securing-container-registry-with-harbor/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="securing-container-registry-with-harbor", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="securing-container-registry-with-harbor")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@container-security-analyst` or `@cybersec-agent`
