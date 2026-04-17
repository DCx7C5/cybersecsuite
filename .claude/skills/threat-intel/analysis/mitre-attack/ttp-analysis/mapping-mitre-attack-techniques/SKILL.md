---
name: mapping-mitre-attack-techniques
description: "'Maps observed adversary behaviors, security alerts, and detection rules to MITRE ATT&CK techniques and sub-techniques"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/mapping-mitre-attack-techniques/SKILL.md"
---
# Mapping Mitre Attack Techniques

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/mapping-mitre-attack-techniques/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="mapping-mitre-attack-techniques", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="mapping-mitre-attack-techniques")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
