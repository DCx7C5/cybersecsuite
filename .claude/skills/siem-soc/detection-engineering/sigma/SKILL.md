---
name: detecting-ai-model-prompt-injection-attacks
description: "'Detects prompt injection attacks targeting LLM-based applications using a multi-layered defense combining regex"
domain: cybersecurity
subdomain: ai-security
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mcpServers: [cybersec]
mitre_attack: []
nist_csf: 
tags: 
source: "/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-ai-model-prompt-injection-attacks/SKILL.md"
---
# Detecting Ai Model Prompt Injection Attacks

> **Source:** `/home/daen/Projects/Anthropic-Cybersecurity-Skills/skills/detecting-ai-model-prompt-injection-attacks/SKILL.md`

## CyberSecSuite Integration

```python
mcp__cybersec__case_open(title="detecting-ai-model-prompt-injection-attacks", type="investigation")
mcp__cybersec__add_finding(title="...", severity="high", description="...")
mcp__cybersec__add_ioc(type="...", value="...", confidence=0.9, source="detecting-ai-model-prompt-injection-attacks")
mcp__cybersec__suggest_mitre(description="...", context="...")
```

## Agent
`@cybersec-agent` → delegates to appropriate specialist.
