---
name: implementing-mimecast-targeted-attack-protection
description: "Deploy Mimecast Targeted Threat Protection including URL Protect, Attachment Protect, Impersonation Protect,"
domain: cybersecurity
subdomain: phishing-defense
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-mimecast-targeted-attack-protection/SKILL.md"
---
# Implementing Mimecast Targeted Attack Protection

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-mimecast-targeted-attack-protection/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-mimecast-targeted-attack-protection", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-mimecast-targeted-attack-protection")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
