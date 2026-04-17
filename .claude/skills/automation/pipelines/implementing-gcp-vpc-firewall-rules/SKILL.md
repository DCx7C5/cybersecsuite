---
name: implementing-gcp-vpc-firewall-rules
description: "'Implementing and auditing GCP VPC firewall rules to enforce network segmentation, restrict ingress and egress"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-gcp-vpc-firewall-rules/SKILL.md"
---
# Implementing Gcp Vpc Firewall Rules

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-gcp-vpc-firewall-rules/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-gcp-vpc-firewall-rules", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-gcp-vpc-firewall-rules")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
