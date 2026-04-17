---
name: implementing-aws-security-hub
description: "'This skill covers deploying AWS Security Hub as a centralized cloud security posture management platform that"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-aws-security-hub/SKILL.md"
---
# Implementing Aws Security Hub

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-aws-security-hub/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-aws-security-hub", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-aws-security-hub")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
