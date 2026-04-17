---
name: securing-api-gateway-with-aws-waf
description: "'Securing API Gateway endpoints with AWS WAF by configuring managed rule groups for OWASP Top 10 protection,"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/securing-api-gateway-with-aws-waf/SKILL.md"
---
# Securing Api Gateway With Aws Waf

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/securing-api-gateway-with-aws-waf/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="securing-api-gateway-with-aws-waf", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="securing-api-gateway-with-aws-waf")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@cloud-security-analyst` or `@cybersec-agent`
