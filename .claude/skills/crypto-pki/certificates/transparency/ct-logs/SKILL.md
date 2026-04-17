---
name: auditing-tls-certificate-transparency-logs
description: "'Monitors Certificate Transparency (CT) logs to detect unauthorized certificate issuance, discover subdomains"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/auditing-tls-certificate-transparency-logs/SKILL.md"
---
# Auditing Tls Certificate Transparency Logs

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/auditing-tls-certificate-transparency-logs/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="auditing-tls-certificate-transparency-logs", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="auditing-tls-certificate-transparency-logs")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@threat-intelligence-analyst` or `@cybersec-agent`
