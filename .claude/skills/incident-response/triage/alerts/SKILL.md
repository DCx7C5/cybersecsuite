---
name: triaging-security-alerts-in-splunk
description: "'Triages security alerts in Splunk Enterprise Security by classifying severity, investigating notable events,"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/triaging-security-alerts-in-splunk/SKILL.md"
---
# Triaging Security Alerts In Splunk

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/triaging-security-alerts-in-splunk/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="triaging-security-alerts-in-splunk", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="triaging-security-alerts-in-splunk")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@soc-operations-analyst` or `@cybersec-agent`
