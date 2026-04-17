---
name: generating-threat-intelligence-reports
description: "'Generates structured cyber threat intelligence reports at strategic, operational, and tactical levels tailored"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/generating-threat-intelligence-reports/SKILL.md"
---
# Generating Threat Intelligence Reports

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/generating-threat-intelligence-reports/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="generating-threat-intelligence-reports", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="generating-threat-intelligence-reports")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
