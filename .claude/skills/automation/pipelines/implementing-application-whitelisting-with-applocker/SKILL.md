---
name: implementing-application-whitelisting-with-applocker
description: "'Implements application whitelisting using Windows AppLocker to restrict unauthorized software execution on endpoints,"
domain: cybersecurity
subdomain: endpoint-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-application-whitelisting-with-applocker/SKILL.md"
---
# Implementing Application Whitelisting With Applocker

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-application-whitelisting-with-applocker/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-application-whitelisting-with-applocker", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-application-whitelisting-with-applocker")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
