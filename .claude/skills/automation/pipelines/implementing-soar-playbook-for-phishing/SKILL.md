---
name: implementing-soar-playbook-for-phishing
description: "Automate phishing incident response using Splunk SOAR REST API to create containers, add artifacts, and trigger"
domain: cybersecurity
subdomain: security-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-soar-playbook-for-phishing/SKILL.md"
---
# Implementing Soar Playbook For Phishing

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-soar-playbook-for-phishing/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-soar-playbook-for-phishing", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-soar-playbook-for-phishing")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
