---
name: implementing-file-integrity-monitoring-with-aide
description: "Configure AIDE (Advanced Intrusion Detection Environment) for file integrity monitoring including baseline creation,"
domain: cybersecurity
subdomain: endpoint-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-file-integrity-monitoring-with-aide/SKILL.md"
---
# Implementing File Integrity Monitoring With Aide

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-file-integrity-monitoring-with-aide/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-file-integrity-monitoring-with-aide", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-file-integrity-monitoring-with-aide")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
