---
name: implementing-container-image-minimal-base-with-distroless
description: "Reduce container attack surface by building application images on Google distroless base images that contain"
domain: cybersecurity
subdomain: container-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-container-image-minimal-base-with-distroless/SKILL.md"
---
# Implementing Container Image Minimal Base With Distroless

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/implementing-container-image-minimal-base-with-distroless/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="implementing-container-image-minimal-base-with-distroless", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="implementing-container-image-minimal-base-with-distroless")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
