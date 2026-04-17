---
name: hunting-for-dcsync-attacks
description: "Detect DCSync attacks by analyzing Windows Event ID 4662 for unauthorized DS-Replication-Get-Changes requests"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hunting-for-dcsync-attacks/SKILL.md"
---
# Hunting For Dcsync Attacks

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hunting-for-dcsync-attacks/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="hunting-for-dcsync-attacks", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="hunting-for-dcsync-attacks")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
