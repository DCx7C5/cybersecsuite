---
name: conducting-mobile-app-penetration-test
description: "'Conducts penetration testing of iOS and Android mobile applications following the OWASP Mobile Application Security"
domain: cybersecurity
subdomain: penetration-testing
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-mobile-app-penetration-test/SKILL.md"
---
# Conducting Mobile App Penetration Test

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-mobile-app-penetration-test/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="conducting-mobile-app-penetration-test", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="conducting-mobile-app-penetration-test")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
