---
name: implementing-azure-defender-for-cloud
description: "'Implementing Microsoft Defender for Cloud to enable cloud security posture management, workload protection across"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-azure-defender-for-cloud/SKILL.md"
---
# Implementing Azure Defender For Cloud

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-azure-defender-for-cloud/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-azure-defender-for-cloud", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-azure-defender-for-cloud")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
