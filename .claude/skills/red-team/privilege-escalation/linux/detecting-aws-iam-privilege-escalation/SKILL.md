---
name: detecting-aws-iam-privilege-escalation
description: "Detect AWS IAM privilege escalation paths using boto3 and Cloudsplaining policy analysis to identify overly permissive"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-aws-iam-privilege-escalation/SKILL.md"
---
# Detecting Aws Iam Privilege Escalation

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-aws-iam-privilege-escalation/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-aws-iam-privilege-escalation", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-aws-iam-privilege-escalation")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
