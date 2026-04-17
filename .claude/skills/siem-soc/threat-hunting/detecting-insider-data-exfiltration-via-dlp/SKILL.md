---
name: detecting-insider-data-exfiltration-via-dlp
description: "'Detects insider data exfiltration by analyzing DLP policy violations, file access patterns, upload volume anomalies,"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-insider-data-exfiltration-via-dlp/SKILL.md"
---
# Detecting Insider Data Exfiltration Via Dlp

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-insider-data-exfiltration-via-dlp/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-insider-data-exfiltration-via-dlp", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-insider-data-exfiltration-via-dlp")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
