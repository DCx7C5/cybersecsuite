---
name: detecting-serverless-function-injection
description: "'Detects and prevents code injection attacks targeting serverless functions (AWS Lambda, Azure Functions, Google"
domain: cybersecurity
subdomain: cloud-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-serverless-function-injection/SKILL.md"
---
# Detecting Serverless Function Injection

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-serverless-function-injection/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-serverless-function-injection", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-serverless-function-injection")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
