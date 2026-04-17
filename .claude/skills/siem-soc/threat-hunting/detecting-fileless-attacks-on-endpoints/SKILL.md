---
name: detecting-fileless-attacks-on-endpoints
description: "'Detects fileless malware and in-memory attacks that execute entirely in RAM without writing persistent files"
domain: cybersecurity
subdomain: endpoint-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-fileless-attacks-on-endpoints/SKILL.md"
---
# Detecting Fileless Attacks On Endpoints

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-fileless-attacks-on-endpoints/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-fileless-attacks-on-endpoints", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-fileless-attacks-on-endpoints")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
