---
name: building-detection-rule-with-splunk-spl
description: "Build effective detection rules using Splunk Search Processing Language (SPL) correlation searches to identify"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-detection-rule-with-splunk-spl/SKILL.md"
---
# Building Detection Rule With Splunk Spl

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-detection-rule-with-splunk-spl/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="building-detection-rule-with-splunk-spl", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-detection-rule-with-splunk-spl")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@soc-operations-analyst` or `@cybersec-agent`
