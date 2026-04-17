---
name: conducting-internal-network-penetration-test
description: "Execute an internal network penetration test simulating an insider threat or post-breach attacker to identify"
domain: cybersecurity
subdomain: penetration-testing
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-internal-network-penetration-test/SKILL.md"
---
# Conducting Internal Network Penetration Test

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/conducting-internal-network-penetration-test/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="conducting-internal-network-penetration-test", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="conducting-internal-network-penetration-test")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
