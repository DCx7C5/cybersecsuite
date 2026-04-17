---
name: conducting-api-security-testing
description: "'Conducts security testing of REST, GraphQL, and gRPC APIs to identify vulnerabilities in authentication, authorization,"
domain: cybersecurity
subdomain: penetration-testing
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-api-security-testing/SKILL.md"
---
# Conducting Api Security Testing

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-api-security-testing/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="conducting-api-security-testing", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="conducting-api-security-testing")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
