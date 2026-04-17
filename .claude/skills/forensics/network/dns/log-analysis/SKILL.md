---
name: analyzing-dns-logs-for-exfiltration
description: "'Analyzes DNS query logs to detect data exfiltration via DNS tunneling, DGA domain communication, and covert"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-dns-logs-for-exfiltration/SKILL.md"
---
# Analyzing Dns Logs For Exfiltration

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-dns-logs-for-exfiltration/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-dns-logs-for-exfiltration", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-dns-logs-for-exfiltration")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@soc-operations-analyst` or `@cybersec-agent`
