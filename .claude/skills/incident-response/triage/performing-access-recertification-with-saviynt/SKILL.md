---
name: performing-access-recertification-with-saviynt
description: "Configure and execute access recertification campaigns in Saviynt Enterprise Identity Cloud to validate user"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-access-recertification-with-saviynt/SKILL.md"
---
# Performing Access Recertification With Saviynt

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-access-recertification-with-saviynt/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-access-recertification-with-saviynt", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-access-recertification-with-saviynt")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
