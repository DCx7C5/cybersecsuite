---
name: implementing-mobile-application-management
description: "'Implements Mobile Application Management (MAM) policies to protect enterprise data on managed and unmanaged"
domain: cybersecurity
subdomain: mobile-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-mobile-application-management/SKILL.md"
---
# Implementing Mobile Application Management

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-mobile-application-management/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-mobile-application-management", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-mobile-application-management")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
