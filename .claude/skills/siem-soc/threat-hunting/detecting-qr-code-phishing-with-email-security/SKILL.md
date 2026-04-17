---
name: detecting-qr-code-phishing-with-email-security
description: "Detect and prevent QR code phishing (quishing) attacks that bypass traditional email security by embedding malicious"
domain: cybersecurity
subdomain: phishing-defense
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-qr-code-phishing-with-email-security/SKILL.md"
---
# Detecting Qr Code Phishing With Email Security

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-qr-code-phishing-with-email-security/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-qr-code-phishing-with-email-security", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-qr-code-phishing-with-email-security")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
