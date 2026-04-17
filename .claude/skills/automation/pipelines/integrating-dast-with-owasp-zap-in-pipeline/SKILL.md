---
name: integrating-dast-with-owasp-zap-in-pipeline
description: "'This skill covers integrating OWASP ZAP (Zed Attack Proxy) for Dynamic Application Security Testing in CI/CD"
domain: cybersecurity
subdomain: devsecops
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/integrating-dast-with-owasp-zap-in-pipeline/SKILL.md"
---
# Integrating Dast With Owasp Zap In Pipeline

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/integrating-dast-with-owasp-zap-in-pipeline/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="integrating-dast-with-owasp-zap-in-pipeline", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="integrating-dast-with-owasp-zap-in-pipeline")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
