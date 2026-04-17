---
name: performing-asset-criticality-scoring-for-vulns
description: "Develop and apply a multi-factor asset criticality scoring model to weight vulnerability prioritization based"
domain: cybersecurity
subdomain: vulnerability-management
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-asset-criticality-scoring-for-vulns/SKILL.md"
---
# Performing Asset Criticality Scoring For Vulns

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-asset-criticality-scoring-for-vulns/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-asset-criticality-scoring-for-vulns", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-asset-criticality-scoring-for-vulns")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
