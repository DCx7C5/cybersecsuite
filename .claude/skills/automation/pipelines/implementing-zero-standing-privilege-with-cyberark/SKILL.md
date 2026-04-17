---
name: implementing-zero-standing-privilege-with-cyberark
description: "Deploy CyberArk Secure Cloud Access to eliminate standing privileges in hybrid and multi-cloud environments using"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-zero-standing-privilege-with-cyberark/SKILL.md"
---
# Implementing Zero Standing Privilege With Cyberark

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-zero-standing-privilege-with-cyberark/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-zero-standing-privilege-with-cyberark", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-zero-standing-privilege-with-cyberark")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
