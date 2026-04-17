---
name: detecting-container-escape-with-falco-rules
description: "Detect container escape attempts in real-time using Falco runtime security rules that monitor syscalls, file"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-container-escape-with-falco-rules/SKILL.md"
---
# Detecting Container Escape With Falco Rules

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-container-escape-with-falco-rules/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="detecting-container-escape-with-falco-rules", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-container-escape-with-falco-rules")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@container-security-analyst` or `@cybersec-agent`
