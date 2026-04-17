---
name: detecting-business-email-compromise
description: "Business Email Compromise (BEC) is a sophisticated fraud scheme where attackers impersonate executives, vendors,"
domain: cybersecurity
subdomain: phishing-defense
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-business-email-compromise/SKILL.md"
---
# Detecting Business Email Compromise

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-business-email-compromise/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-business-email-compromise", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-business-email-compromise")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
