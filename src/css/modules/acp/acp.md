# @acp - Agent Client Protocol Runtime

**Location**: `src/css/modules/acp/`
**Phase ownership**: Phase 42 - ACP + LSP + Marketplace Implementation
**Tracking rule**: `.plan/session.db` is authoritative for status. This
document owns executable implementation details for ACP runtime work.

---

## Purpose

`@acp` is the primary runtime owner for:
- ACP transport and JSON-RPC session protocol handling
- ACP session lifecycle + update stream orchestration
- ACP permission-request bridging to approvals policy
- LSP runtime bridge under ACP-controlled session context

`@jetbrains` remains a legacy adapter surface and compatibility bridge; it is
not the long-term owner for ACP/LSP protocol runtime.

## Ownership Boundary

| Area | Owner |
|------|-------|
| ACP protocol and session runtime | `modules/acp` |
| MCP runtime connect/discover/call | `modules/mcps` |
| Marketplace catalog/install state | `core/marketplace` |
| Approval policy and decisions | `modules/approvals` |
| Legacy IDE adapter and compatibility endpoints | `modules/jetbrains` |

## Phase 42 Todo Map

| Todo ID | Status in `session.db` | Contract owned here |
|---------|------------------------|---------------------|
| `acp42-module-bootstrap` | done | Create ACP module owner surface and document cutover from JetBrains-first planning. |
| `acp42-spec-v1-contract` | pending | ACP v1 contract for initialize, auth, session methods, session/update variants, and permission flow. |
| `acp42-stdio-transport-runtime` | pending | JSON-RPC stdio transport runtime with process lifecycle and correlation. |
| `acp42-initialize-negotiation` | pending | Version/capability negotiation with strict compatibility checks. |
| `acp42-authentication-capabilities` | pending | Authentication capability wiring and logout flow. |
| `acp42-session-method-surface` | pending | Implement session/new+prompt+cancel+load+list+resume+close request handling. |
| `acp42-session-update-stream-model` | pending | Typed session/update notification model and fan-out. |
| `acp42-permission-request-bridge` | pending | session/request_permission integration with approvals. |
| `acp42-mcp-server-passthrough` | pending | Server-scoped MCP descriptor passthrough via `modules/mcps`. |
| `lsp42-transport-runtime` | pending | LSP stdio JSON-RPC runtime under ACP session context. |
| `lsp42-lifecycle-handshake` | pending | LSP initialize/initialized/shutdown/exit handshake and capability cache. |
| `lsp42-document-sync` | pending | didOpen/didChange/didClose/didSave synchronization pipeline. |
| `lsp42-language-features` | pending | hover/completion/definition/references/rename/codeAction/formatting wrappers. |
| `lsp42-diagnostics-pipeline` | pending | publishDiagnostics ingestion and streaming updates. |

## Numbered Execution Order

1. Lock ACP v1 request/response contracts and capability flags.
2. Implement ACP transport + initialize/auth/session lifecycle.
3. Implement session/update event model + permission bridge + MCP passthrough.
4. Implement LSP transport/lifecycle/sync/features/diagnostics under ACP.
5. Validate compatibility boundaries with marketplace install hooks and legacy
   JetBrains adapter routes.

## Validation Gates

- `ruff check src/css/modules/acp src/css/modules/mcps src/css/modules/approvals`
- `uvx basedpyright` on touched ACP/LSP files
- targeted ACP session method tests and protocol fixture replay
- runtime checks that `mcp:{server_id}:{tool_name}` identity is preserved
- marketplace install/uninstall integration checks for ACP/LSP artifacts
