---
name: implementing-network-intrusion-prevention-with-suricata
description: "Deploy and configure Suricata as a network intrusion prevention system with custom rules, Emerging Threats rulesets,"
domain: cybersecurity
subdomain: network-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-network-intrusion-prevention-with-suricata/SKILL.md"
---
# Implementing Network Intrusion Prevention With Suricata

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-network-intrusion-prevention-with-suricata/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-network-intrusion-prevention-with-suricata", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-network-intrusion-prevention-with-suricata")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
