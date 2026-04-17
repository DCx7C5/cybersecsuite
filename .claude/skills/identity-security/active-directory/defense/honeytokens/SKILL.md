---
name: deploying-active-directory-honeytokens
description: "'Deploys deception-based honeytokens in Active Directory including fake privileged accounts with AdminCount=1,"
domain: cybersecurity
subdomain: deception-technology
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-active-directory-honeytokens/SKILL.md"
---
# Deploying Active Directory Honeytokens

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-active-directory-honeytokens/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="deploying-active-directory-honeytokens", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="deploying-active-directory-honeytokens")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@deception-technology-analyst` or `@cybersec-agent`
