---
name: performing-adversary-in-the-middle-phishing-detection
description: "Detect and respond to Adversary-in-the-Middle (AiTM) phishing attacks that use reverse proxy kits like EvilProxy,"
domain: cybersecurity
subdomain: phishing-defense
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-adversary-in-the-middle-phishing-detection/SKILL.md"
---
# Performing Adversary In The Middle Phishing Detection

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-adversary-in-the-middle-phishing-detection/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-adversary-in-the-middle-phishing-detection", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-adversary-in-the-middle-phishing-detection")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
