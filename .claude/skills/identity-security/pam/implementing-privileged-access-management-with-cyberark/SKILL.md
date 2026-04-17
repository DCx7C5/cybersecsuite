---
name: implementing-privileged-access-management-with-cyberark
description: "Deploy CyberArk Privileged Access Management to discover, vault, rotate, and monitor privileged credentials across"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-privileged-access-management-with-cyberark/SKILL.md"
---
# Implementing Privileged Access Management With Cyberark

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-privileged-access-management-with-cyberark/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-privileged-access-management-with-cyberark", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-privileged-access-management-with-cyberark")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
