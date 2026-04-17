---
name: implementing-cloud-dlp-for-data-protection
description: "'Implementing Cloud Data Loss Prevention (DLP) using Amazon Macie, Azure Information Protection, and Google Cloud"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-cloud-dlp-for-data-protection/SKILL.md"
---
# Implementing Cloud Dlp For Data Protection

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-cloud-dlp-for-data-protection/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-cloud-dlp-for-data-protection", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-cloud-dlp-for-data-protection")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
