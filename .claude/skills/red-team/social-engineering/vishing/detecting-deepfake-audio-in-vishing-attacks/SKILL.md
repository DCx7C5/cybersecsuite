---
name: detecting-deepfake-audio-in-vishing-attacks
description: "'Detects AI-generated deepfake audio used in voice phishing (vishing) attacks by extracting spectral features"
domain: cybersecurity
subdomain: social-engineering-defense
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-deepfake-audio-in-vishing-attacks/SKILL.md"
---
# Detecting Deepfake Audio In Vishing Attacks

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-deepfake-audio-in-vishing-attacks/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-deepfake-audio-in-vishing-attacks", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-deepfake-audio-in-vishing-attacks")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
