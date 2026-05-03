# GitHub Copilot SDK & Management APIs

**Provider**: GitHub (Copilot + Management APIs)  
**Status**: ✅ Production (Copilot SDK: Public Preview April 2026) | **Last Updated**: 2026-05-03  
**OpenAPI Compatible**: ❌ No (JSON-RPC + Proprietary APIs)

---

## 🆕 CRITICAL UPDATE: GitHub NOW HAS OFFICIAL COPILOT SDK (2026)

### Previous Understanding ❌ OUTDATED
- ❌ "No official SDK or REST API"
- ❌ "Only IDE plugins available"
- ❌ "Unofficial wrappers violate ToS"

### Current Reality ✅ 2026
- ✅ **`github-copilot-sdk`** officially released (Python, TypeScript, Go, .NET, Java)
- ✅ PyPI package: `pip install github-copilot-sdk`
- ✅ Programmatic access to Copilot's agentic engine
- ✅ Public Preview since April 2026

---

## SDK Features

| Feature | Supported | Notes |
|---------|-----------|-------|
| Streaming | ✅ | Real-time event streaming |
| Vision | ✅ | Image/file attachments via blob upload |
| Tool Use | ✅ | Custom tool definition + invocation |
| JSON Mode | ✅ | Structured output |
| Async/Await | ✅ | Native async/await support |
| Agentic Workflows | ✅ | Multi-turn sessions, reasoning |
| MCP Support | ✅ | Model Context Protocol compatible |

---

## GitHub Copilot SDK (Python) - NEW

### What It Is
Official Python SDK for **programmatically embedding Copilot's agentic workflows** into applications.

### Installation
```bash
pip install github-copilot-sdk
python -m pip install --upgrade github-copilot-sdk
```

**Requirements**:
- Python 3.11+
- GitHub Copilot CLI installed and authenticated (in PATH)
- GitHub CLI: `gh` command available

### Key Features
✅ **Agentic Workflows**: Multi-turn sessions, tool invocation, streaming
✅ **Session Management**: Create sessions, manage lifecycle
✅ **Custom Tools**: Define tools using decorators + Pydantic
✅ **Streaming**: Real-time event streaming
✅ **Blob Attachments**: Send files/attachments to Copilot
✅ **JSON-RPC Communication**: Direct communication with Copilot CLI
✅ **Async/Await**: Full async support with asyncio
✅ **Event Handling**: Subscribe to agent events (message, tool use, etc.)

---

## Built-in Tools & Methods

### Core Session Management
- `CopilotClient()` — Main client (context manager)
- `client.create_session()` — Create new session
- `session.send()` — Send text message
- `session.events()` — Async event stream
- `session.close()` — Close session

### Event Types
- `assistant.message` — Response messages
- `tool_use` — Tool invocation event
- `thinking` — Extended thinking events
- `completion` — Completion markers

### Custom Tools
- `Tool` — Base tool class
- `ToolParameter` — Tool parameter definition
- `ToolChoice` — Tool selection strategy
- Pydantic `BaseModel` for input schemas

### Attachments
- `session.upload_blob()` — Upload file/data
- `Blob` — Attachment data structure

### Error Handling
- `CopilotError` — Base error
- `AuthenticationError` — Auth failed
- `SessionError` — Session management errors
- `ToolError` — Tool invocation errors

---

## Usage Examples

### Basic Chat
```python
import asyncio
from copilot import CopilotClient

async def main():
    async with CopilotClient() as client:
        # Create a session with a model
        async with await client.create_session(model="gpt-5") as session:
            # Send a message
            await session.send("Explain the builder pattern in Python")
            
            # Stream events
            async for event in session.events():
                if event.type.value == "assistant.message":
                    print(event.data.content)

asyncio.run(main())
```

### With Custom Tools
```python
from copilot import CopilotClient, Tool, ToolParameter
from pydantic import BaseModel

class CalculatorInput(BaseModel):
    a: float
    b: float

class Calculator(Tool):
    async def invoke(self, params: CalculatorInput) -> str:
        return f"Result: {params.a + params.b}"

async def main():
    async with CopilotClient() as client:
        # Register custom tool
        calculator = Calculator(
            name="add_numbers",
            description="Add two numbers",
            input_schema=CalculatorInput
        )
        
        async with await client.create_session(
            model="gpt-5",
            tools=[calculator]
        ) as session:
            await session.send("What is 5 + 3?")
            
            async for event in session.events():
                if event.type.value == "assistant.message":
                    print(event.data.content)

asyncio.run(main())
```

### With File Attachments
```python
import asyncio
from pathlib import Path
from copilot import CopilotClient

async def main():
    async with CopilotClient() as client:
        async with await client.create_session(model="gpt-5") as session:
            # Upload a file
            file_data = Path("analysis.json").read_bytes()
            await session.upload_blob(file_data, filename="analysis.json")
            
            # Ask about the file
            await session.send("Analyze this security report")
            
            async for event in session.events():
                if event.type.value == "assistant.message":
                    print(event.data.content)

asyncio.run(main())
```

---

## Model Support

**Available Models**:
- `gpt-5` — Latest Copilot model (recommended)
- `gpt-4o` — Alternative model
- Others — Check Copilot CLI for available models

---

## GitHub Copilot Extensions (Apps) - SUNSETTING ⏰

### Timeline
| Date | Event |
|------|-------|
| Feb 2025 | Copilot Extensions (Apps) GA for all subscribers |
| Sept 24, 2025 | **No new Copilot Extensions allowed** |
| Nov 3-7, 2025 | Brownout period (interruptions) |
| **Nov 10, 2025** | **All Copilot Extensions (Apps) DISABLED** ⛔ |

### What's Happening
Copilot Extensions (built as GitHub Apps) are being discontinued in favor of:
1. **MCP (Model Context Protocol)** — New open standard for agentic tools
2. **Copilot CLI Extensions** — Local project extensions
3. **Copilot SDK** — Direct programmatic integration

### Action Required
If maintaining a Copilot Extension (App):
- **Migrate to MCP** before November 10, 2025
- OR use CLI extensions for local-only needs
- OR use Copilot SDK for programmatic integration

---

## GitHub Copilot CLI Extensions - Local Integration

### Purpose
Local, project-specific CLI extensions for Copilot CLI.

### Features
- **Local installation**: `.github/extensions/` in your project
- **JSON-RPC communication**: Communicate with Copilot CLI
- **Written in Node.js**: Extensible with TypeScript
- **No marketplace needed**: Private to your project/org
- **Deep customization**: Inject tools, intercept actions, custom workflows

### Example Structure
```
my-project/
├── .github/
│   └── extensions/
│       ├── package.json
│       ├── index.js
│       └── tools/
│           ├── lint.js
│           ├── test.js
│           └── custom-analyzer.js
```

### Use Case
Local development tooling, custom linters, project-specific agents, team-wide CLI extensions.

---

## MCP (Model Context Protocol) - NEW STANDARD

### What is MCP?
Open protocol for connecting **any AI model** (Copilot, Claude, etc.) to **any tool/data source**.

### Benefits
- **Cross-platform**: Build once, deploy to Copilot, Claude, other AI platforms
- **Standardized**: No vendor lock-in
- **Tool composition**: Chain tools across platforms
- **Enterprise-ready**: Clear security boundaries

### Integration Points
- GitHub Copilot (replacing Copilot Extensions)
- Anthropic Claude Code
- Other agentic AI platforms

### Resources
- **MCP GitHub**: https://github.com/modelcontextprotocol
- **MCP Registry**: https://mcp.github.com
- **Docs**: https://modelcontextprotocol.io/

---

## GitHub REST API for Copilot - Management Only

### What's Available
✅ **User/License Management**:
- Assign/revoke Copilot licenses
- List Copilot seats
- Get usage metrics

❌ **NOT Available**:
- No programmatic code completions API
- No REST endpoint for suggestions
- No headless Copilot

### Example: List Copilot Seats
```python
import requests

ORG = "my-org"
TOKEN = "ghp_..."  # GitHub PAT

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

response = requests.get(
    f"https://api.github.com/orgs/{ORG}/copilot/billing/seats",
    headers=headers
)
print(response.json())
```

### Management API Endpoints
- `GET /orgs/{org}/copilot/billing/seats` — List seats
- `POST /orgs/{org}/copilot/billing/seats` — Assign seat
- `DELETE /orgs/{org}/copilot/billing/seats/{username}` — Revoke seat
- `GET /orgs/{org}/copilot/billing/seats/{username}` — Get seat info

### Documentation
- [GitHub Copilot REST API](https://docs.github.com/en/rest/copilot)
- [Enterprise Admin API](https://docs.github.com/en/rest/enterprise-admin)

---

## Microsoft 365 Copilot - Enterprise Integration

### Purpose
For **business/enterprise** scenarios (NOT code generation).

### What's Offered
- **Chat API (Preview)**: Multi-turn chat grounded in M365 data
- **Retrieval API**: Search organizational data
- **Export API**: Prepare data for Copilot

### Requirements
- Microsoft 365 E3/E5 license
- Microsoft 365 Copilot subscription
- Azure AD registration
- REST API via Microsoft Graph (`/beta/copilot/chat`)

### Python SDK
```bash
pip install microsoft-agents-m365copilot
```

### Not Relevant For
- GitHub code suggestions
- Developer tooling
- Open-source projects

---

## SDK Type Classification

### Into Our 4 SDK Types Framework

**Type 1️⃣: Official SDK Libraries**
- ✅ `github-copilot-sdk` (Python, TypeScript, Go, .NET, Java)
- **Status**: Public Preview (April 2026)
- **PyPI**: https://pypi.org/project/github-copilot-sdk/
- **Features**: Agentic workflows, tool invocation, streaming, sessions
- **Requires**: Copilot CLI installed locally

**Type 2️⃣: Local/Offline SDKs**
- ✅ Copilot CLI + SDK (runs locally, needs authentication)
- **Execution**: Local machine only
- **Privacy**: Server communication required (but no persistent data)
- **Uses**: Requires active GitHub subscription/license

**Type 3️⃣: Browser Plugin Protocol**
- ❌ **No browser plugin for Copilot**: IDE plugins only (VS Code, JetBrains, etc.)
- ✅ **Alternative**: Use Copilot SDK for web apps

**Type 4️⃣: Custom REST Wrappers**
- ✅ GitHub REST API (for license/seat management only)
- **Status**: Management API, NOT code generation API
- **Pattern**: Standard HTTP requests + GitHub PAT

---

## For CyberSecSuite Integration

### Decision: Which Copilot to Use?

**Use Case 1: Code Generation/Suggestions**
- **Use**: `github-copilot-sdk` (Type 1)
- **Pattern**: Create CopilotSDKClient(api_service_type=Type1)
- **Config**: Requires Copilot CLI installed + GitHub auth
- **Availability**: Only if user has GitHub Copilot subscription

**Use Case 2: Enterprise/Microsoft 365 Integration**
- **Use**: `microsoft-agents-m365copilot` (Type 1 variant)
- **Pattern**: Create M365CopilotSDKClient()
- **Config**: Requires Azure AD + M365 Copilot license
- **Availability**: Only for enterprise M365 customers

**Use Case 3: License/Seat Management**
- **Use**: GitHub REST API (Type 4 custom wrapper)
- **Pattern**: Create GitHubManagementClient(github_token)
- **Config**: GitHub PAT with admin:org_copilot scope
- **Availability**: For GitHub org admins

### Implementation Pattern

Update `provider-types-mapping.md`:

```markdown
## Type 1️⃣: Official SDK Libraries - GITHUB/COPILOT UPDATE

| Provider | SDK Package | Status | Features |
|----------|-------------|--------|----------|
| **GitHub Copilot** | `github-copilot-sdk` | ✅ Public Preview | Agentic workflows, tool invocation, streaming, sessions |
| **Microsoft 365 Copilot** | `microsoft-agents-m365copilot` | 🚧 Preview | Enterprise chat, M365 data integration |
| ... (others) | ... | ... | ... |

## Type 4️⃣: Custom REST Wrappers

| Provider | Endpoint | Status | Type |
|----------|----------|--------|------|
| **GitHub Copilot Management** | `api.github.com/orgs/{org}/copilot/billing/seats` | ✅ Production | License/seat management |
| ... (others) | ... | ... | ... |
```

---

## Deprecations & Changes

### Copilot Extensions (Apps) ⛔ DEPRECATED
- **Sunsetting**: Nov 10, 2025
- **Replacement**: MCP or Copilot SDK
- **Action**: Migrate if using

### Old Unofficial Wrappers ⚠️ NOT RECOMMENDED
- `copilot-api` (PyPI) — Unofficial, no longer needed
- Other reverse-engineered solutions — Violate ToS
- **Use**: Official `github-copilot-sdk` instead

---

## Resources & Documentation

- **GitHub Copilot SDK Repo**: https://github.com/github/copilot-sdk
- **Python Samples**: https://github.com/github/copilot-sdk/tree/main/python
- **PyPI**: https://pypi.org/project/github-copilot-sdk/
- **Blog**: Copilot SDK in public preview (April 2026)
- **MCP GitHub**: https://github.com/modelcontextprotocol
- **MCP Registry**: https://mcp.github.com

---

## Key Takeaways

✅ **GitHub NOW has an official Copilot SDK** (April 2026 release)
✅ **Programmatic access IS available** via `github-copilot-sdk`
✅ **Public Preview status** means it's production-ready but may evolve
✅ **Requires Copilot CLI** + GitHub authentication
✅ **Full feature set**: Agentic workflows, tool invocation, streaming
⏰ **Copilot Extensions sunsetting** Nov 10, 2025 (migrate to MCP/SDK)
📦 **MCP emerging** as cross-AI-platform standard
❌ **GitHub REST API is management-only** (no code generation endpoint)

---

**Status**: ✅ Complete | **Last Updated**: 2026-05-03
