---
name: implementing-privileged-session-monitoring
description: "'Implements privileged session monitoring and recording using Privileged Access Management (PAM) solutions, focusing"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-privileged-session-monitoring/SKILL.md"
---
# Implementing Privileged Session Monitoring

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-privileged-session-monitoring/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-privileged-session-monitoring", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-privileged-session-monitoring")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
