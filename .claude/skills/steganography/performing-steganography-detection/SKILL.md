---
name: performing-steganography-detection
description: "Detect and extract hidden data embedded in images, audio, and other media files using steganalysis tools to uncover"
domain: cybersecurity
subdomain: digital-forensics
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-steganography-detection/SKILL.md"
---
# Performing Steganography Detection

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/performing-steganography-detection/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="performing-steganography-detection", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="performing-steganography-detection")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
