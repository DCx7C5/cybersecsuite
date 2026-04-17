---
name: performing-phishing-simulation-with-gophish
description: "GoPhish is an open-source phishing simulation framework used by security teams to conduct authorized phishing"
domain: cybersecurity
subdomain: phishing-defense
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-phishing-simulation-with-gophish/SKILL.md"
---
# Performing Phishing Simulation With Gophish

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-phishing-simulation-with-gophish/SKILL.md`
> Full technique details in source. This stub adds CyberSecSuite integration.

## CyberSecSuite Integration

```python
# Open a case before starting
mcp__cybersec__case_open(title="performing-phishing-simulation-with-gophish", type="investigation")

# Persist findings to PostgreSQL
mcp__cybersec__add_finding(title="...", severity="high", description="...", mitre_techniques=[])

# Log IOCs discovered
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-phishing-simulation-with-gophish")

# Suggest MITRE mapping
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
Invoke via: `@phishing-defense-analyst` or `@cybersec-agent`
