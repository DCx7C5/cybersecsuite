---
name: analyzing-azure-activity-logs-for-threats
description: "'Queries Azure Monitor activity logs and sign-in logs via azure-monitor-query to detect suspicious administrative"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-azure-activity-logs-for-threats/SKILL.md"
---
# Analyzing Azure Activity Logs For Threats

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-azure-activity-logs-for-threats/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-azure-activity-logs-for-threats", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-azure-activity-logs-for-threats")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@security-operations-analyst` or `@cybersec-agent`
