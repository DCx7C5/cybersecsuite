# MCP_DEV_INSTRUCTIONS.md

**Master Project Instructions**  
**MCP Component Development Framework**  
*For Dual Orchestration Suite Compatibility*

**This is entirely about writing components with both orchestration suites.**  
**We write several MCP servers, skills, agents or plugins.**

## Project Overview

The goal of this project is to produce a complete library of production-ready, cross-compatible components built on the
**Model Context Protocol (MCP)** standard.

Every deliverable must work natively and optimally in **both orchestration suites** without code forks, heavy
conditionals, or suite-specific hacks.

**Target deliverables per sprint:**

- 4–8 **MCP Servers**
- 10–15 **Skills**
- 3–5 **Agents / Agent Teams**
- 2–3 **Plugins** (bundled one-click packages)

All components follow the official MCP specification and common patterns used by Claude Code, Cursor, VS Code Copilot,
LangGraph, CrewAI, and any MCP-native orchestration platform.

## Repository Structure (Your AI/ Folder)

AI/
├── mcps/ # MCP Servers (with INSTRUCTIONS.md)
├── skills/ # Skills (with INSTRUCTIONS.md)
├── agents/
│ ├── subagents/ # Individual specialist agents
│ ├── agent-teams/ # Multi-agent collaboration definitions
│ └── ORCHESTRATION-PATTERNS.md
├── plugins/ # Bundled one-click packages
├── docs/ # Component catalog + usage guides
├── tests/ # Cross-suite test harness
├── templates/ # Starter templates
└── MCP_DEV_INSTRUCTIONS.md # ← This file

## Component Types & Creation Guidelines

### 1. MCP Servers (mcps/)

**Purpose**: Expose tools, resources, and prompts via MCP.

**Repeatable Steps**:

1. Create folder `mcps/<domain-name-server>/`
2. Use FastMCP: `server = FastMCP("domain-name-server")`
3. Decorate tools with rich descriptions + examples + strict schemas
4. Add resources/prompts as needed
5. Run via SSE
6. Test registration and execution in **both** suites
7. Document registration steps in README.md

**Priority Domains**: GitHub/GitLab, Filesystem, Databases, API Gateways, CI/CD, Custom Business Tools.

### 2. Skills (skills/)

**Purpose**: Reusable procedural knowledge packages.

**Repeatable Steps**:

1. Create folder `skills/<skill-name>/`
2. Write `SKILL.md` with exact sections:
    - Purpose
    - When to Use
    - Step-by-Step Workflow
    - Prompt Templates
    - Required MCP Servers
    - Examples & Test Cases
3. Add supporting files (schemas, examples)
4. Test import and execution in **both** suites

**Priority Skills**: Code Review, Multi-Agent Task Breakdown, API Design, Data Analysis, Customer Support, Security
Checks, UI/UX Prototyping.

### 3. Agents & Agent Teams (agents/)

**Purpose**: Orchestrator and specialist agents that dynamically use MCP servers and skills.

**Repeatable Steps**:

1. Choose pattern from `ORCHESTRATION-PATTERNS.md`
2. Create file in `subagents/` or `agent-teams/`
3. Define: Role, Available Skills, Callable MCP Servers, Planner/Evaluator Loop, Handoff Rules
4. Use MCP resources for shared memory
5. Test full orchestration in **both** suites

### 4. Plugins (plugins/)

**Purpose**: One-click installable bundles.

**Repeatable Steps**:

1. Create folder `plugins/<plugin-name>/`
2. Write `manifest.json` (servers, skills, agents)
3. Add `INSTALL.md` with steps for both suites
4. Package as zip or GitHub repo
5. Test one-click installation in **both** suites

## Development Workflow (Repeat for Every Component)

1. Define use case & required MCP servers/skills
2. Create component using category-specific INSTRUCTIONS.md
3. Test in isolation
4. Verify end-to-end in **Suite 1**
5. Verify end-to-end in **Suite 2**
6. Add cross-suite test script
7. Package & version (semantic versioning)
8. Commit to monorepo

## Best Practices

- Rich tool descriptions + multiple examples
- Progressive disclosure everywhere
- Graceful degradation for new MCP features
- Monitor token usage and latency across both suites
- Independent versioning of MCP servers
- Always document exact registration/import steps for each suite

## Next Immediate Actions

1. Confirm names of the two orchestration suites if needed
2. Create first 3 MCP servers using `mcps/INSTRUCTIONS.md`
3. Create first 5 skills using `skills/INSTRUCTIONS.md`
4. Build first agents using `agents/ORCHESTRATION-PATTERNS.md`
5. Start packaging first plugin

---

```python
```

```markdown

**This is entirely about writing components with both orchestration suites.**  
**We write several MCP servers, skills, agents or plugins.**