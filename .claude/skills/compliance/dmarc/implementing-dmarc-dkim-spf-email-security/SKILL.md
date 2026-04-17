---
name: implementing-dmarc-dkim-spf-email-security
description: "SPF, DKIM, and DMARC form the three pillars of email authentication. Together they prevent domain spoofing, validate"
domain: cybersecurity
subdomain: phishing-defense
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-dmarc-dkim-spf-email-security/SKILL.md"
---
# Implementing Dmarc Dkim Spf Email Security

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-dmarc-dkim-spf-email-security/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-dmarc-dkim-spf-email-security", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-dmarc-dkim-spf-email-security")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
