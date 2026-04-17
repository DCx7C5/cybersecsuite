---
name: monitoring-darkweb-sources
description: "'Monitors dark web forums, marketplaces, paste sites, and ransomware leak sites for mentions of organizational"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/monitoring-darkweb-sources/SKILL.md"
---
# Monitoring Darkweb Sources

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/monitoring-darkweb-sources/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="monitoring-darkweb-sources", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="monitoring-darkweb-sources")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
