---
name: implementing-secret-scanning-with-gitleaks
description: "'This skill covers implementing Gitleaks for detecting and preventing hardcoded secrets in git repositories."
domain: cybersecurity
subdomain: devsecops
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-secret-scanning-with-gitleaks/SKILL.md"
---
# Implementing Secret Scanning With Gitleaks

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-secret-scanning-with-gitleaks/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-secret-scanning-with-gitleaks", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-secret-scanning-with-gitleaks")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
