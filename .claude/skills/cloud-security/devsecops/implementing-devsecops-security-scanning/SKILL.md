---
name: implementing-devsecops-security-scanning
description: "'Integrates Static Application Security Testing (SAST), Dynamic Application Security Testing (DAST), and Software"
domain: cybersecurity
subdomain: application-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-devsecops-security-scanning/SKILL.md"
---
# Implementing Devsecops Security Scanning

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-devsecops-security-scanning/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-devsecops-security-scanning", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-devsecops-security-scanning")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
