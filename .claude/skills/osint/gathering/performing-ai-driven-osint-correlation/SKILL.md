---
name: performing-ai-driven-osint-correlation
description: "Use AI and LLM-based reasoning to correlate findings across multiple OSINT sources—username enumeration, email"
domain: cybersecurity
subdomain: threat-intelligence
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-ai-driven-osint-correlation/SKILL.md"
---
# Performing Ai Driven Osint Correlation

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-ai-driven-osint-correlation/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-ai-driven-osint-correlation", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-ai-driven-osint-correlation")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
