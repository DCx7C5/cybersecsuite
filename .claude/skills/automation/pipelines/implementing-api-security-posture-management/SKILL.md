---
name: implementing-api-security-posture-management
description: "Implement API Security Posture Management to continuously discover, classify, and score APIs based on risk while"
domain: cybersecurity
subdomain: api-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-api-security-posture-management/SKILL.md"
---
# Implementing Api Security Posture Management

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-api-security-posture-management/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-api-security-posture-management", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-api-security-posture-management")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
