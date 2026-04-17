---
name: implementing-mitre-attack-coverage-mapping
description: "Implement MITRE ATT&CK coverage mapping to identify detection gaps, prioritize rule development, and measure"
domain: cybersecurity
subdomain: soc-operations
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-mitre-attack-coverage-mapping/SKILL.md"
---
# Implementing Mitre Attack Coverage Mapping

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-mitre-attack-coverage-mapping/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-mitre-attack-coverage-mapping", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-mitre-attack-coverage-mapping")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
