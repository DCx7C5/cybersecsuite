---
name: implementing-aqua-security-for-container-scanning
description: "Deploy Aqua Security's Trivy scanner to detect vulnerabilities, misconfigurations, secrets, and license issues"
domain: cybersecurity
subdomain: devsecops
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-aqua-security-for-container-scanning/SKILL.md"
---
# Implementing Aqua Security For Container Scanning

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-aqua-security-for-container-scanning/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-aqua-security-for-container-scanning", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-aqua-security-for-container-scanning")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
