---
name: analyzing-windows-event-logs-in-splunk
description: "'Analyzes Windows Security, System, and Sysmon event logs in Splunk to detect authentication attacks, privilege"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-windows-event-logs-in-splunk/SKILL.md"
---
# Analyzing Windows Event Logs In Splunk

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-windows-event-logs-in-splunk/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-windows-event-logs-in-splunk", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-windows-event-logs-in-splunk")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@soc-operations-analyst` or `@cybersec-agent`
