---
name: building-cloud-siem-with-sentinel
description: "'This skill covers deploying Microsoft Sentinel as a cloud-native SIEM and SOAR platform for centralized security"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-cloud-siem-with-sentinel/SKILL.md"
---
# Building Cloud Siem With Sentinel

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/building-cloud-siem-with-sentinel/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="building-cloud-siem-with-sentinel", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="building-cloud-siem-with-sentinel")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@cloud-security-analyst` or `@cybersec-agent`
