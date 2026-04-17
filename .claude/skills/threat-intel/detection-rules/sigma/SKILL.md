---
name: building-detection-rules-with-sigma
description: "'Builds vendor-agnostic detection rules using the Sigma rule format for threat detection across SIEM platforms"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-detection-rules-with-sigma/SKILL.md"
---
# Building Detection Rules With Sigma

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-detection-rules-with-sigma/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="building-detection-rules-with-sigma", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-detection-rules-with-sigma")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@soc-operations-analyst` or `@cybersec-agent`
