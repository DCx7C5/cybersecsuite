---
name: detecting-cryptomining-in-cloud
description: "'This skill teaches security teams how to detect and respond to unauthorized cryptocurrency mining operations"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-cryptomining-in-cloud/SKILL.md"
---
# Detecting Cryptomining In Cloud

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-cryptomining-in-cloud/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-cryptomining-in-cloud", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-cryptomining-in-cloud")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
