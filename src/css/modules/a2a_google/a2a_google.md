# @a2a_google — Google A2A Protocol Integration

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This document owns the executable Google A2A specification.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.modules.a2a_internal` | → consumes | Internal A2A request/result envelopes before federating to Google A2A |
| `css.modules.agents` | ← consumed by | Agents that need to reach external Google-hosted A2A peers |
| `css.core.resilience` | → consumes | Retry / backoff policy for external network calls |
| `css.core.events` | ← instruments | External A2A call lifecycle, latency, and failures |
| `css.core.cache` | note | No direct KV-cache dependency planned; cache prompt/retrieval state elsewhere, not in this transport adapter |

---

## Purpose

- Enable CyberSecSuite agents to communicate with external Google A2A agents
- Translate between `a2a_internal` message flow (internal) and Google A2A protocol (external)
- Handle OAuth/service account authentication
- Implement retry + rate limiting (50-500ms latency)
- Graceful fallback if Google A2A unavailable

---

## Architecture

```
CyberSecSuite Agent
    ↓ [CSS A2A Internal]
GoogleA2AAdapter
    ↓ [Google A2A Protocol]
Google Cloud Agent
```

---

## Use Case: Communication with External Agents

```
Our System                      Google Cloud
│                               │
├─ Our Agent (Worker)           ├─ Google Agent
│  ├─ Needs: Google API key     │  └─ Registered in Google A2A
│  ├─ Has: Service account      │
│  └─ Can reach: Google A2A API │
│                               │
└─ A2A Request (HTTPS)
   Our Agent → Google A2A → Google Agent
   └─ Response: HTTPS ← Google Agent ← Google A2A
```

---

## Use Case: Federated Analysis

```
Our System (CyberSecSuite)     Google Cloud (External Agents)
│                              │
├─ Team-Security (Our)         ├─ GoogleSecurityAgent
│  ├─ Worker-1                 │  └─ Registered, A2A enabled
│  └─ Worker-2                 │
│                              │
└─ Scenario: Correlate our findings with Google agent findings
   
   Step 1: Our Worker-1 sends findings to GoogleSecurityAgent
   Step 2: GoogleSecurityAgent processes + sends response
   Step 3: Our Worker-1 receives + correlates findings
   Step 4: Result: Federated analysis (ours + Google's)
```

---

## Implementation

```python
# src/css/modules/a2a_google/adapter.py
class GoogleA2AAdapter:
    """Adapter for Google Auth2App direct agent communication"""
    
    def __init__(self, api_key: str, project_id: str):
        self.api_key = api_key
        self.project_id = project_id
        self.client = GoogleA2AClient(api_key, project_id)
    
    async def send_message(self, 
                          recipient_agent_id: str,
                          message: dict,
                          timeout_sec: int = 30) -> dict:
        """Send message to Google-registered agent via A2A"""
        
        payload = {
            "recipient": {
                "agentId": recipient_agent_id,
                "projectId": self.project_id
            },
            "message": message,
            "timeoutSeconds": timeout_sec
        }
        
        # Call Google A2A API (HTTPS)
        response = await self.client.send_request(payload)
        return response
    
    async def receive_messages(self, 
                               queue_timeout_sec: int = 60) -> list[dict]:
        """Poll Google A2A for messages addressed to our agents"""
        
        messages = await self.client.poll_queue(
            project_id=self.project_id,
            timeout_sec=queue_timeout_sec
        )
        return messages

# src/css/modules/a2a_google/endpoints.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/google-a2a", tags=["google-a2a"])

@router.post("/send")
async def send_to_google_agent(recipient_id: str, message: dict):
    """Send message to Google-registered agent"""
    adapter = GoogleA2AAdapter(api_key=config.GOOGLE_A2A_KEY, project_id=config.GOOGLE_PROJECT_ID)
    response = await adapter.send_message(recipient_id, message)
    return response

@router.get("/receive")
async def receive_from_google_agent():
    """Receive messages from Google agents"""
    adapter = GoogleA2AAdapter(api_key=config.GOOGLE_A2A_KEY, project_id=config.GOOGLE_PROJECT_ID)
    messages = await adapter.receive_messages()
    return {"messages": messages}
```

---

## Comparison: CSS A2A vs Google A2A

| Aspect | CSS A2A | Google A2A |
|--------|---------|-----------|
| **Location** | Same system | Third-party (Google Cloud) |
| **Transport** | IPC (pipes, sockets) | HTTPS/REST API |
| **Latency** | <1ms (local) | 50-500ms (network) |
| **Dependency** | None (internal) | Google Cloud API |
| **Auth** | Process isolation | API key + OAuth |
| **Scale** | Within CyberSecSuite | Any Google-registered agent |
| **Use Case** | High-speed local A2A | Federated external analysis |
| **Cost** | Free (local) | Google Cloud pricing |
| **Reliability** | 100% (our control) | Subject to Google uptime |

---

## When to Use Google A2A

**Use Google A2A When:**
- ✅ Need external agent capabilities (Google's tools)
- ✅ Federated analysis (combine ours + Google's)
- ✅ Scalability (leverage Google infrastructure)
- ✅ Specific Google agent integrations required
- ✅ Acceptable latency (100-500ms)

---

## Implementation Checklist

- [ ] Implement Google A2A adapter (convert CSS A2A ↔ Google A2A)
- [ ] Add authentication manager (OAuth + service account)
- [ ] Add retry + rate limiting logic
- [ ] Create integration tests with Google A2A mock
- [ ] Add logger initialization in `__init__.py`
- [ ] Document authentication setup (API key, service account, OAuth)

---

## Module Pattern

```python
# src/css/modules/a2a_google/__init__.py
"""Google A2A protocol integration for external agent communication."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .adapter import GoogleA2AAdapter
from .auth import GoogleAuthManager

__all__ = ['GoogleA2AAdapter', 'GoogleAuthManager']
```

## Routing Surface

- `urls.py` is the module route entrypoint used to initialize endpoint state and mount both routers:
  - `init_a2a_endpoints(...)`
  - `app.include_router(router)`
  - `app.include_router(root_router)`

---

**Status**: 🟡 Partial (adapter implementation pending) | **Last Updated**: 2026-05-03
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: Query `.plan/session.db` for current status; retain A2A implementation detail in this local document.

---

## 🔄 Sync Reminder

> **STATUS AUTHORITY**: Query `.plan/session.db` for live todo progress.
>
> - This file defines the implementation contract, not completion state.
> - Update tracker state as required by `.plan/rules.md`.
> - **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE
> - See `.plan/rules.md` CRITICAL section for full rules
>
> **Pattern rules enforced here**:
> - `__all__` lives ONLY in `__init__.py` (never in types.py, enums.py, endpoints.py)
> - Never mix `@dataclass` with `ABC` on the same class
> - Use `msgspec.Struct` for value types, `Protocol` for structural contracts (Phase 6)
> - HTTP clients: always `aiohttp`, never `httpx`
> - Package manager: always `uv`/`bun`, never `pip`/`npm`
