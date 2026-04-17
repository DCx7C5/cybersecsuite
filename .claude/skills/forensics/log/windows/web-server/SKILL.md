---
name: analyzing-web-server-logs-for-intrusion
description: "Parse Apache and Nginx access logs to detect SQL injection attempts, local file inclusion, directory traversal,"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-web-server-logs-for-intrusion/SKILL.md"
---
# Analyzing Web Server Logs For Intrusion

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/analyzing-web-server-logs-for-intrusion/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="analyzing-web-server-logs-for-intrusion", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="analyzing-web-server-logs-for-intrusion")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@security-operations-analyst` or `@cybersec-agent`
