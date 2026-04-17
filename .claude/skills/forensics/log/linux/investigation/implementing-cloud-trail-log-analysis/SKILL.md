---
name: implementing-cloud-trail-log-analysis
description: "'Implementing AWS CloudTrail log analysis for security monitoring, threat detection, and forensic investigation"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-cloud-trail-log-analysis/SKILL.md"
---
# Implementing Cloud Trail Log Analysis

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-cloud-trail-log-analysis/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-cloud-trail-log-analysis", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-cloud-trail-log-analysis")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
