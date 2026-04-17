---
name: detecting-broken-object-property-level-authorization
description: "Detect and test for OWASP API3:2023 Broken Object Property Level Authorization vulnerabilities including excessive"
domain: cybersecurity
subdomain: api-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-broken-object-property-level-authorization/SKILL.md"
---
# Detecting Broken Object Property Level Authorization

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-broken-object-property-level-authorization/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-broken-object-property-level-authorization", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-broken-object-property-level-authorization")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
