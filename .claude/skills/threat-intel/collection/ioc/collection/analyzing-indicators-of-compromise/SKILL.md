---
name: analyzing-indicators-of-compromise
description: "'Analyzes indicators of compromise (IOCs) including IP addresses, domains, file hashes, URLs, and email artifacts"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-indicators-of-compromise/SKILL.md"
---
# Analyzing Indicators Of Compromise

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-indicators-of-compromise/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="analyzing-indicators-of-compromise", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-indicators-of-compromise")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
