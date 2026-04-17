---
name: implementing-secrets-scanning-in-ci-cd
description: "Integrate gitleaks and trufflehog into CI/CD pipelines to detect leaked secrets before deployment"
domain: cybersecurity
subdomain: devsecops
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-secrets-scanning-in-ci-cd/SKILL.md"
---
# Implementing Secrets Scanning In Ci Cd

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-secrets-scanning-in-ci-cd/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-secrets-scanning-in-ci-cd", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-secrets-scanning-in-ci-cd")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
