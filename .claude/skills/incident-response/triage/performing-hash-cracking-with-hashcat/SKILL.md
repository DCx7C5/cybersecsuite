---
name: performing-hash-cracking-with-hashcat
description: "Hash cracking is an essential skill for penetration testers and security auditors to evaluate password strength."
domain: cybersecurity
subdomain: cryptography
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-hash-cracking-with-hashcat/SKILL.md"
---
# Performing Hash Cracking With Hashcat

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-hash-cracking-with-hashcat/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-hash-cracking-with-hashcat", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-hash-cracking-with-hashcat")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
