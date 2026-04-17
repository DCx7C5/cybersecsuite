---
name: detecting-container-escape-attempts
description: "Container escape is a critical attack technique where an adversary breaks out of container isolation to access"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-container-escape-attempts/SKILL.md"
---
# Detecting Container Escape Attempts

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-container-escape-attempts/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-container-escape-attempts", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-container-escape-attempts")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
