---
name: detecting-aws-credential-exposure-with-trufflehog
description: "'Detecting exposed AWS credentials in source code repositories, CI/CD pipelines, and configuration files using"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-aws-credential-exposure-with-trufflehog/SKILL.md"
---
# Detecting Aws Credential Exposure With Trufflehog

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-aws-credential-exposure-with-trufflehog/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-aws-credential-exposure-with-trufflehog", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-aws-credential-exposure-with-trufflehog")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
