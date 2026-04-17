---
name: detecting-container-drift-at-runtime
description: "Detect unauthorized modifications to running containers by monitoring for binary execution drift, file system"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-container-drift-at-runtime/SKILL.md"
---
# Detecting Container Drift At Runtime

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-container-drift-at-runtime/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-container-drift-at-runtime", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-container-drift-at-runtime")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
