---
name: implementing-security-chaos-engineering
description: "'Implements security chaos engineering experiments that deliberately disable or degrade security controls to"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-security-chaos-engineering/SKILL.md"
---
# Implementing Security Chaos Engineering

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-security-chaos-engineering/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-security-chaos-engineering", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-security-chaos-engineering")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
