# A2A Protocol — CyberSec Suite

Implementation of the [Google Agent-to-Agent (A2A)](https://google.github.io/A2A/) protocol for the CyberSec Suite.

---

## Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                      Multi-Agent System                              │
│                                                                      │
│   Client ──► OrchestratorAgent ──► AgentRegistry                    │
│                     │                    │                            │
│              skill routing          ┌────┴─────────────┐             │
│                     │               │                   │             │
│                     ▼               ▼                   ▼             │
│            PythonDeveloper    CppDeveloper      CybersecAgent        │
│            :8001              :8002             :8000                 │
│                                                                      │
│   .claude/agents/*.md ──► agent_loader ──► AgentRegistry             │
│   ├── cybersec-agent (orchestrator, default)                         │
│   ├── cybersec-analyst                                               │
│   ├── filesystem-analyst                                             │
│   ├── kernel-analyst                                                 │
│   ├── memory-analyst                                                 │
│   ├── network-analyst                                                │
│   ├── persistence-analyst                                            │
│   ├── threat-modeler                                                 │
│   └── teams/ (blue-team, red-team, purple-team)                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Single Agent

```python
from starlette.applications import Starlette
from a2a import CybersecA2AAgent, A2AServer

agent = CybersecA2AAgent(base_url="http://localhost:8000")
app = Starlette()
app.mount("/", A2AServer(agent).router)
```

### Multi-Agent Orchestrator

```python
from a2a import OrchestratorAgent, A2AServer
from a2a.dev_agents import create_default_registry

# Pre-wire all agents (local cards + .claude/agents/*.md definitions)
registry = create_default_registry(
    python_url="http://localhost:8001",
    cpp_url="http://localhost:8002",
    cybersec_url="http://localhost:8000",
    load_claude_agents=True,  # loads .claude/agents/*.md (default: True)
)

# Or discover remote agents via their AgentCards
await registry.discover("http://remote-agent:8003")

orchestrator = OrchestratorAgent(registry=registry, base_url="http://localhost:9000")
app.mount("/", A2AServer(orchestrator).router)
```

### Load from .claude/agents/ directly

```python
from pathlib import Path
from a2a import AgentRegistry

# Auto-detect project root and load all .claude/agents/*.md + teams/
registry = AgentRegistry.from_cybersecsuite()

# Or specify path explicitly
registry = AgentRegistry.from_agents_dir(
    Path("/path/to/.claude/agents"), recurse=True
)

# Find the default agent (hunter)
default = registry.find_default()
orchestrator = registry.find_orchestrator()

# Find by alias (e.g. "blue" → blue-team, if loaded with recurse)
agent = registry.find_by_name("hunter")
```

### Client — Delegation Commands

```python
from a2a import A2AClient

async with A2AClient("http://localhost:9000") as client:

    # Auto-route by keywords
    task = await client.send_task("write a Python CVE parser")
    task = await client.send_task("implement a ring buffer in C++")

    # Explicit agent by name
    task = await client.send_task("@agent PythonDeveloper: write a BLAKE2b hasher")
    task = await client.send_task("@agent CppDeveloper: optimize this hot loop")

    # Explicit skill ID
    task = await client.send_task("@skill cpp-review: check this buffer handling")

    # Fan-out: all agents in parallel
    task = await client.send_task("@fanout implement a Bloom filter")

    # Pipeline: chain agents sequentially
    task = await client.send_task("@pipeline CybersecAgent -> PythonDeveloper -> CppDeveloper")

    # List all agents
    task = await client.send_task("list agents")
```

---

## Orchestration Commands

| Command | Format | Description |
|---------|--------|-------------|
| Auto-route | `<text>` | Best-matching agent selected automatically |
| By name | `@agent <Name>: <prompt>` | Delegate to a specific named agent |
| By skill | `@skill <skill-id>: <prompt>` | Delegate to agents with that skill |
| Fan-out | `@fanout <prompt>` | All agents in parallel, results merged |
| Pipeline | `@pipeline A -> B -> C` | Sequential chain, output of A feeds B |
| List | `list agents` | Show all registered agents and skills |

---

## Specialized Agents

### `PythonDeveloper` (:8001)

| Skill ID        | Tags                     | Triggered by             |
|-----------------|--------------------------|--------------------------|
| `python-write`  | python, code, script     | write, create, implement |
| `python-review` | python, audit, security  | review, audit, check     |
| `python-debug`  | python, debug, error     | debug, fix, traceback    |
| `python-test`   | python, pytest, coverage | test, pytest, spec       |

### `CppDeveloper` (:8002)

| Skill ID       | Tags                  | Triggered by                |
|----------------|-----------------------|-----------------------------|
| `cpp-write`    | cpp, c++, develop     | write, implement, build     |
| `cpp-review`   | cpp, memory, security | review, audit, memory, leak |
| `cpp-debug`    | cpp, segfault, asan   | debug, crash, segfault      |
| `cpp-optimize` | cpp, perf, simd       | optimize, performance, fast |

### `CybersecAgent` (:8000)

| Skill ID        | Tags               | Triggered by           |
|-----------------|--------------------|------------------------|
| `cve-lookup`    | cve, vulnerability | cve-, vulnerability    |
| `ioc-analysis`  | ioc, threat-intel  | ioc, ip, hash, domain  |
| `mitre-attack`  | mitre, ttp         | mitre, att&ck, t1      |
| `artifact-sign` | artifact, signing  | sign, verify, artifact |
| `threat-model`  | threat-model, risk | threat model, risk     |

---

## Module Reference

### `a2a/enums.py`

| Enum          | Values                                                                      |
|---------------|-----------------------------------------------------------------------------|
| `TaskState`   | `submitted`, `working`, `input-required`, `completed`, `failed`, `canceled` |
| `MessageRole` | `user`, `agent`                                                             |
| `PartType`    | `text`, `file`, `data`                                                      |
| `AuthScheme`  | `none`, `ed25519`, `bearer`, `api_key`                                      |

---

### `a2a/models.py`

#### Message Parts

| Model      | Description                                                     |
|------------|-----------------------------------------------------------------|
| `TextPart` | Plain text — `{type: "text", text: "..."}`                      |
| `FilePart` | File attachment — `{type: "file", file: {name, mime_type, bytes |uri}}` |
| `DataPart` | Structured JSON — `{type: "data", data: {...}}`                 |

#### Core Models

```python
class Message:
    role: MessageRole          # "user" | "agent"
    parts: List[Part]          # TextPart | FilePart | DataPart
    metadata: dict | None

class Task:
    id: str
    session_id: str | None
    status: TaskStatus         # state + optional message + timestamp
    history: List[Message]
    artifacts: List[TaskArtifact]
    metadata: dict | None

class AgentCard:
    name: str
    description: str
    url: str
    version: str
    capabilities: AgentCapabilities   # streaming, push_notifications
    authentication: AgentAuthentication
    skills: List[AgentSkill]
```

#### JSON-RPC

```python
class JSONRPCRequest:
    jsonrpc: "2.0"
    id: str | int | None
    method: str
    params: dict | None

class JSONRPCResponse:
    jsonrpc: "2.0"
    id: str | int | None
    result: Any | None
    error: JSONRPCError | None
```

---

### `a2a/task_store.py` — `TaskStore`

In-memory task registry. Replace with a persistent backend (Redis, DB) for production.

```python
store = TaskStore()

task  = store.create(params)                          # Create
task  = store.get(task_id)                            # Retrieve
task  = store.update_status(task_id, state, message)  # Transition state
task  = store.add_artifact(task_id, artifact)         # Append output
task  = store.cancel(task_id)                         # Cancel
tasks = store.list_tasks(session_id=None)             # List all
```

---

### `a2a/agent.py` — `BaseA2AAgent`

Abstract base class. Subclass and implement `execute()`.

```python
class MyAgent(BaseA2AAgent):

    async def execute(self, task: Task, message: Message) -> None:
        text = self._extract_text(message)  # Not in base — implement in subclass
        # ... process ...
        self._reply(task.id, "Done!")                     # text reply → COMPLETED
        self._add_text_artifact(task.id, result, "out")   # add artifact
        self._fail(task.id, "Something went wrong")       # → FAILED

    async def stream(self, task, message) -> AsyncIterator[Task]:
        # Optional: override for streaming
        self.store.update_status(task.id, TaskState.WORKING)
        yield self.store.get(task.id)
        await self.execute(task, message)
        yield self.store.get(task.id)
```

---

### `a2a/server.py` — `A2AServer`

ASGI router. Mounts three endpoints:

| Endpoint                  | Method | Description       |
|---------------------------|--------|-------------------|
| `/.well-known/agent.json` | GET    | Serve `AgentCard` |
| `/a2a`                    | POST   | JSON-RPC dispatch |
| `/a2a/stream/{task_id}`   | GET    | SSE streaming     |

#### JSON-RPC Methods

| Method                       | Params                       | Returns |
|------------------------------|------------------------------|---------|
| `tasks/send`                 | `TaskSendParams`             | `Task`  |
| `tasks/get`                  | `TaskQueryParams`            | `Task`  |
| `tasks/cancel`               | `TaskIdParams`               | `Task`  |
| `tasks/pushNotification/set` | `TaskPushNotificationConfig` | config  |
| `tasks/pushNotification/get` | `TaskIdParams`               | config  |
| `tasks/resubscribe`          | `TaskIdParams`               | `Task`  |

#### Error Codes

| Code     | Name                             |
|----------|----------------------------------|
| `-32700` | Parse error                      |
| `-32600` | Invalid request                  |
| `-32601` | Method not found                 |
| `-32602` | Invalid params                   |
| `-32603` | Internal error                   |
| `-32001` | Task not found                   |
| `-32002` | Task not cancelable              |
| `-32003` | Push notifications not supported |
| `-32004` | Unsupported operation            |
| `-32006` | Auth required                    |

---

### `a2a/client.py` — `A2AClient`

Async HTTP client. Always use as async context manager.

```python
async with A2AClient(
    base_url="http://localhost:8000",
    timeout=30.0,
    headers={"Authorization": "Bearer <token>"},
) as client:

    # Agent discovery
    card = await client.get_agent_card()

    # Simple text task
    task = await client.send_task("Describe T1059")

    # Task with full Message control
    from a2a import Message, DataPart, MessageRole, PartType
    task = await client.send_task_with_message(
        Message(
            role=MessageRole.USER,
            parts=[DataPart(type=PartType.DATA, data={"cve_id": "CVE-2024-1234"})],
        )
    )

    # Query status
    task = await client.get_task(task.id, history_length=10)

    # Cancel
    task = await client.cancel_task(task.id)

    # Stream
    async for update in client.stream_task("Analyze IP 1.2.3.4"):
        print(update.status.state, update.artifacts)
```

---

### `a2a/cybersec_agent.py` — `CybersecA2AAgent`

Concrete cybersecurity agent. Skill routing is keyword-based on message text.

| Keyword trigger                          | Skill            | Handler                |
|------------------------------------------|------------------|------------------------|
| `cve-`, `cve `, `vulnerability`          | CVE Lookup       | `_handle_cve`          |
| `ioc`, `ip `, `hash`, `domain`, `url`    | IOC Analysis     | `_handle_ioc`          |
| `mitre`, `att&ck`, `technique`, `t1`     | MITRE ATT&CK     | `_handle_mitre`        |
| `sign`, `verify`, `artifact`             | Artifact Signing | `_handle_artifact`     |
| `threat model`, `attack surface`, `risk` | Threat Modeling  | `_handle_threat_model` |

**Wire in database models to complete each skill handler:**

```python
# _handle_cve → db.models.cve.CveEntry
# _handle_ioc → db.models.ioc.Ioc + db.models.ioc_entry.IocEntry
# _handle_mitre → db.models.mitre_technique.MitreTechnique
# _handle_artifact → crypto.artifact_manager.ArtifactManager
# _handle_threat_model → db.models.threat_intel.ThreatIntel
```

---

## Authentication

The agent supports **Ed25519** request signing (configured in `AgentAuthentication`).

To verify incoming requests, add middleware to `A2AServer`:

```python
from crypto.ssl_signer import SSLArtifactSigner

signer = SSLArtifactSigner(public_key_path="/etc/dystopian-crypto/keys/agent-public.pem")

# In middleware: verify the Authorization header contains a valid Ed25519 token
is_valid, payload = signer.verify_artifact(request.headers.get("Authorization", ""))
if not is_valid:
    return JSONResponse({"error": "Unauthorized"}, status_code=401)
```

---

## Task Lifecycle

```
           tasks/send
               │
               ▼
          [submitted]
               │
         agent picks up
               │
               ▼
           [working]
               │
        ┌──────┴───────┐
        │              │
        ▼              ▼
  [input-required]  artifacts added
        │              │
   user replies        ▼
        │          [completed]
        └──────►       │
                   (terminal)

  any state ──cancel──► [canceled]
  any state ──error───► [failed]
```

---

## SSE Streaming Format

```
data: {"id": "...", "status": {"state": "working"}, ...}

data: {"id": "...", "status": {"state": "completed"}, "artifacts": [...]}

data: [DONE]
```

---

## File Structure

```
src/a2a/
├── __init__.py          # Public API exports
├── enums.py             # TaskState, MessageRole, PartType, AuthScheme
├── models.py            # All Pydantic data models
├── task_store.py        # In-memory task registry
├── agent.py             # BaseA2AAgent abstract class
├── agent_loader.py      # .claude/agents/*.md → AgentCard + ClaudeAgentCard
├── server.py            # ASGI JSON-RPC server + SSE
├── client.py            # Async HTTP client
├── registry.py          # AgentRegistry with .claude metadata support
├── orchestrator.py      # OrchestratorAgent — multi-agent routing
├── cybersec_agent.py    # Concrete cybersecurity agent
├── dev_agents.py        # Python/C++ developer agents + create_default_registry
└── README.md
```



---

## Agent SDK Integration (Phase A2)

> ⚠️ **Not yet complete.** `agent_sdk.py` is present but `execute()` methods in `dev_agents.py` and `cybersec_agent.py` return stub strings. Phase A2 wires them to `run_agent_query()`.

When complete, the execution path will be:

```python
# a2a/agent_sdk.py
from a2a.agent_sdk import run_agent_query, build_agent_options

# Inside BaseA2AAgent.execute():
options = build_agent_options(mcp_servers=..., allowed_tools=...)
result = await run_agent_query(task.message, options=options)
```

This connects the A2A external protocol path (JSON-RPC) with the Agent SDK internal execution path (Claude API + in-process MCP tools).

See [docs/architecture.md](../../docs/architecture.md) for the full two-path explanation.
