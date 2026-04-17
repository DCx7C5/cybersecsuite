---
name: implementing-aws-macie-for-data-classification
description: "Implement Amazon Macie to automatically discover, classify, and protect sensitive data in S3 buckets using machine"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-aws-macie-for-data-classification/SKILL.md"
---
# Implementing Aws Macie For Data Classification

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-aws-macie-for-data-classification/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-aws-macie-for-data-classification", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-aws-macie-for-data-classification")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
