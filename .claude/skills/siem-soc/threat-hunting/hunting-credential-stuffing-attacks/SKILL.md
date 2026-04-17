---
name: hunting-credential-stuffing-attacks
description: "'Detects credential stuffing attacks by analyzing authentication logs for login velocity anomalies, ASN diversity,"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hunting-credential-stuffing-attacks/SKILL.md"
---
# Hunting Credential Stuffing Attacks

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hunting-credential-stuffing-attacks/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="hunting-credential-stuffing-attacks", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="hunting-credential-stuffing-attacks")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
