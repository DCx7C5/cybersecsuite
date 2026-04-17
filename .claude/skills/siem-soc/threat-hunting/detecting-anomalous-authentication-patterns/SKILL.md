---
name: detecting-anomalous-authentication-patterns
description: "'Detects anomalous authentication patterns using UEBA analytics, statistical baselines, and machine learning"
domain: cybersecurity
subdomain: identity-access-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-anomalous-authentication-patterns/SKILL.md"
---
# Detecting Anomalous Authentication Patterns

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-anomalous-authentication-patterns/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-anomalous-authentication-patterns", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-anomalous-authentication-patterns")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
