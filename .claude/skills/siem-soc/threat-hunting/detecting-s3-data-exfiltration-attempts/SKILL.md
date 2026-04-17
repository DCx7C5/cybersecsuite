---
name: detecting-s3-data-exfiltration-attempts
description: "'Detecting data exfiltration attempts from AWS S3 buckets by analyzing CloudTrail S3 data events, VPC Flow Logs,"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-s3-data-exfiltration-attempts/SKILL.md"
---
# Detecting S3 Data Exfiltration Attempts

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-s3-data-exfiltration-attempts/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-s3-data-exfiltration-attempts", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-s3-data-exfiltration-attempts")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
