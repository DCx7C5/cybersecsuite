---
name: bypassing-authentication-with-forced-browsing
description: "Discovering and accessing unprotected pages, APIs, and administrative interfaces by enumerating URLs and bypassing"
domain: cybersecurity
subdomain: web-application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/bypassing-authentication-with-forced-browsing/SKILL.md"
---
# Bypassing Authentication With Forced Browsing

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/bypassing-authentication-with-forced-browsing/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="bypassing-authentication-with-forced-browsing", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="bypassing-authentication-with-forced-browsing")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
