---
name: implementing-cloud-workload-protection
description: "'Implements cloud workload protection using boto3 and google-cloud APIs for runtime security monitoring, process"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-cloud-workload-protection/SKILL.md"
---
# Implementing Cloud Workload Protection

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-cloud-workload-protection/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-cloud-workload-protection", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-cloud-workload-protection")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
