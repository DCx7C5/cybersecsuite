---
name: detecting-credential-dumping-techniques
description: "Detect LSASS credential dumping, SAM database extraction, and NTDS.dit theft using Sysmon Event ID 10, Windows"
domain: cybersecurity
subdomain: threat-detection
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-credential-dumping-techniques/SKILL.md"
---
# Detecting Credential Dumping Techniques

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-credential-dumping-techniques/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-credential-dumping-techniques", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-credential-dumping-techniques")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
