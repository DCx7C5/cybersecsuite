---
name: performing-gcp-security-assessment-with-forseti
description: "'Performing comprehensive security assessments of Google Cloud Platform environments using Forseti Security,"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-gcp-security-assessment-with-forseti/SKILL.md"
---
# Performing Gcp Security Assessment With Forseti

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-gcp-security-assessment-with-forseti/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-gcp-security-assessment-with-forseti", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-gcp-security-assessment-with-forseti")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
