---
name: performing-threat-modeling-with-owasp-threat-dragon
description: "Use OWASP Threat Dragon to create data flow diagrams, identify threats using STRIDE and LINDDUN methodologies,"
domain: cybersecurity
subdomain: devsecops
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-threat-modeling-with-owasp-threat-dragon/SKILL.md"
---
# Performing Threat Modeling With Owasp Threat Dragon

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-threat-modeling-with-owasp-threat-dragon/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-threat-modeling-with-owasp-threat-dragon", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-threat-modeling-with-owasp-threat-dragon")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
