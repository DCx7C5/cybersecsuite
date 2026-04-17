---
name: performing-content-security-policy-bypass
description: "Analyze and bypass Content Security Policy implementations to achieve cross-site scripting by exploiting misconfigurations,"
domain: cybersecurity
subdomain: web-application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-content-security-policy-bypass/SKILL.md"
---
# Performing Content Security Policy Bypass

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-content-security-policy-bypass/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-content-security-policy-bypass", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-content-security-policy-bypass")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
