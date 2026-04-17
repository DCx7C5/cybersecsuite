---
name: detecting-t1003-credential-dumping-with-edr
description: "Detect OS credential dumping techniques targeting LSASS memory, SAM database, NTDS.dit, and cached credentials"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-t1003-credential-dumping-with-edr/SKILL.md"
---
# Detecting T1003 Credential Dumping With Edr

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-t1003-credential-dumping-with-edr/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-t1003-credential-dumping-with-edr", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-t1003-credential-dumping-with-edr")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
