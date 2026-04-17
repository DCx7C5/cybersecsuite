---
name: detecting-typosquatting-packages-in-npm-pypi
description: "'Detects typosquatting attacks in npm and PyPI package registries by analyzing package name similarity using"
domain: cybersecurity
subdomain: supply-chain-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-typosquatting-packages-in-npm-pypi/SKILL.md"
---
# Detecting Typosquatting Packages In Npm Pypi

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-typosquatting-packages-in-npm-pypi/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-typosquatting-packages-in-npm-pypi", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-typosquatting-packages-in-npm-pypi")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
