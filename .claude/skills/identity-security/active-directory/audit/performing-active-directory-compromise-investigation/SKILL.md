---
name: performing-active-directory-compromise-investigation
description: "Investigate Active Directory compromise by analyzing authentication logs, replication metadata, Group Policy"
domain: cybersecurity
subdomain: incident-response
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-active-directory-compromise-investigation/SKILL.md"
---
# Performing Active Directory Compromise Investigation

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-active-directory-compromise-investigation/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-active-directory-compromise-investigation", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-active-directory-compromise-investigation")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
