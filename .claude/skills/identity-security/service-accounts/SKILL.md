---
name: performing-service-account-audit
description: "Audit service accounts across enterprise infrastructure to identify orphaned, over-privileged, and non-compliant"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-service-account-audit/SKILL.md"
---
# Performing Service Account Audit

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-service-account-audit/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-service-account-audit", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-service-account-audit")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@identity-access-management-analyst` or `@cybersec-agent`
