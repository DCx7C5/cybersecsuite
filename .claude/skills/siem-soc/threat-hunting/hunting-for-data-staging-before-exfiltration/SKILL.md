---
name: hunting-for-data-staging-before-exfiltration
description: "Detect data staging activity before exfiltration by monitoring for archive creation with 7-Zip/RAR, unusual temp"
domain: cybersecurity
subdomain: threat-hunting
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hunting-for-data-staging-before-exfiltration/SKILL.md"
---
# Hunting For Data Staging Before Exfiltration

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/hunting-for-data-staging-before-exfiltration/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="hunting-for-data-staging-before-exfiltration", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="hunting-for-data-staging-before-exfiltration")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
