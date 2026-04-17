---
name: performing-active-directory-penetration-test
description: "Conduct a focused Active Directory penetration test to enumerate domain objects, discover attack paths with BloodHound,"
domain: cybersecurity
subdomain: penetration-testing
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-active-directory-penetration-test/SKILL.md"
---
# Performing Active Directory Penetration Test

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-active-directory-penetration-test/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-active-directory-penetration-test", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-active-directory-penetration-test")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
