---
name: deploying-osquery-for-endpoint-monitoring
description: "'Deploys and configures osquery for real-time endpoint monitoring using SQL-based queries to inspect running"
domain: cybersecurity
subdomain: endpoint-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: 
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-osquery-for-endpoint-monitoring/SKILL.md"
---
# Deploying Osquery For Endpoint Monitoring

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/deploying-osquery-for-endpoint-monitoring/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="deploying-osquery-for-endpoint-monitoring", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=)

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="deploying-osquery-for-endpoint-monitoring")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@endpoint-security-analyst` or `@cybersec-agent`
