---
name: integrating-sast-into-github-actions-pipeline
description: "'This skill covers integrating Static Application Security Testing (SAST) tools—CodeQL and Semgrep—into GitHub"
domain: cybersecurity
subdomain: devsecops
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/integrating-sast-into-github-actions-pipeline/SKILL.md"
---
# Integrating Sast Into Github Actions Pipeline

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/integrating-sast-into-github-actions-pipeline/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="integrating-sast-into-github-actions-pipeline", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="integrating-sast-into-github-actions-pipeline")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
