---
name: performing-active-directory-forest-trust-attack
description: "Enumerate and audit Active Directory forest trust relationships using impacket for SID filtering analysis, trust"
domain: cybersecurity
subdomain: red-team
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-active-directory-forest-trust-attack/SKILL.md"
---
# Performing Active Directory Forest Trust Attack

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-active-directory-forest-trust-attack/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-active-directory-forest-trust-attack", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-active-directory-forest-trust-attack")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
