# @jetbrains - IDE PyCharm Integration

**Location**: `src/css/modules/jetbrains/`
**Phase ownership**: Phase 38 - IDE PyCharm
**Tracking rule**: `.plan/session.db` is authoritative for todo status; this
document owns the executable implementation details for the package.

---

## Purpose

`@jetbrains` connects CyberSecSuite with PyCharm IDE tooling. It exposes file
operations, search, code analysis, run configurations, refactoring, and
database operations through the app's module pattern so endpoints and agents
can interact with an IDE connector programmatically.

Phase 42 direction: `@jetbrains` is treated as a **legacy compatibility
bridge** for IDE-facing integration, while ACP/LSP protocol runtime ownership
is moving to `src/css/modules/acp/`.

## Design Decisions

- The module is a thin typed facade over PyCharm tool capabilities.
- `PyCharmToolClient` owns all IDE interactions.
- `DatabaseClient` wraps IDE database connection operations separately.
- Endpoints use `init_clients()` for dependency injection (no global singletons).
- Future: agent tools can import and use `PyCharmToolClient` directly.

## Current Code Reality

| File             | Status  | Reality |
|------------------|---------|---------|
| `__init__.py`    | ✅ done | Exports all public types, enums, exceptions via `__all__` |
| `types.py`       | ✅ done | 14 msgspec.Struct types: FileLocation, RunConfiguration, SearchQuery, etc. |
| `enums.py`       | ✅ done | IDEToolCategory, SearchMode, OperationStatus, IDEConnectionState, RefactorKind |
| `exceptions.py`  | ✅ done | IDEError, IDEConnectionError, IDEOperationError, IDETimeoutError, IDENotAvailableError |
| `client.py`      | scaffolded | `PyCharmToolClient` methods exist but currently return placeholder successful/empty results. |
| `database.py`    | scaffolded | `DatabaseClient` methods exist but currently return placeholder results. |
| `endpoints.py`   | scaffolded | FastAPI router at `/api/ide/*` forwards calls through initialized clients. |
| `jetbrains.md` | maintained | This local specification. |

The existing Python surfaces are interface scaffolding, not functioning IDE
integration. Real connector invocation and error/availability behavior remain
implementation work even where the tracker records scaffold todos as done.

## Type and Client Contract

| Surface | Required contract |
|---------|-------------------|
| Value types | `FileLocation`, `RunConfiguration`, `SearchQuery`, `SearchMatch`, `IDEOperationResult`, `CodeAnalysisProblem`, database result types, `SymbolInfo`, and `ProjectInfo` remain `msgspec.Struct` API shapes. |
| IDE enums | Tool category, search mode, operation status, connection state, and refactor kind define outward API vocabulary. |
| File/client operations | Read/get/create/replace/reformat/open file actions call the IDE connector and map failures to typed operation errors. |
| Search/analysis | Text, regex, symbol, file discovery, problem inspection, symbol lookup, and project build results return real IDE output. |
| Run/refactor/project | List/execute run configurations, rename symbols, inspect project info, and list directory trees through the connector. |
| Database client | List connections/schemas/objects, describe objects, execute queries, preview tables, and test connections through IDE database tooling. |

## API Surface

| Route family | Required behavior |
|--------------|-------------------|
| `/api/ide/status` | Report initialized connector/database availability. |
| `/api/ide/files/*` | Read, create, replace, open, and reformat IDE-managed files. |
| `/api/ide/search/*` | Text/regex/symbol/file search. |
| `/api/ide/analysis/*` | Problems, symbol information, and project build invocation. |
| `/api/ide/run/*` | Run configuration listing and execution. |
| `/api/ide/refactor/*` | Refactor actions beginning with safe rename. |
| `/api/ide/project/*` | Project metadata and directory tree lookup. |
| `/api/ide/database/*` | Database discovery, query, and table preview routes. |

## Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.modules.tools` | → registers | IDE tools become agent-callable tools in ToolRegistry |
| `css.core.asgi` | → started by | ASGI lifespan calls `init_clients()` |
| `css.modules.agents` | → consumed by | Agents use IDE tools for code operations |

## Todos

| Todo ID | Outcome | Live tracker status checked 2026-05-25 |
|---------|---------|-----------------------------------------|
| `idepycharm-foundation` | Package types/enums/exceptions/exports scaffold. | done |
| `idepycharm-client` | `PyCharmToolClient` method scaffold. | done |
| `idepycharm-endpoints` | `/api/ide/*` router scaffold. | done |
| `idepycharm-database` | `DatabaseClient` method scaffold. | done |
| `idepycharm-agent-wiring` | Initialize real clients at lifespan and register agent-callable tools. | pending |

## Phase 42 LSP Bridge Todo Map

| Todo ID | Status in `session.db` | Contract owned here |
|---------|------------------------|---------------------|
| `acp42-module-bootstrap` | done | Cutover planning ownership to `modules/acp` while retaining JetBrains adapter compatibility. |
| `lsp42-transport-runtime` | pending | Implemented by `modules/acp`; JetBrains consumes stable bridge APIs only. |
| `lsp42-lifecycle-handshake` | pending | Implemented by `modules/acp`; JetBrains remains compatibility consumer. |
| `lsp42-document-sync` | pending | Implemented by `modules/acp`; JetBrains consumes document-state bridge APIs. |
| `lsp42-language-features` | pending | Implemented by `modules/acp`; JetBrains maps results into IDE-oriented contracts. |
| `lsp42-diagnostics-pipeline` | pending | Implemented by `modules/acp`; JetBrains reads diagnostic feeds for UI/automation. |

## Completion Boundary

After lifespan/tool wiring, validate that scaffold methods invoke actual
connector capabilities instead of returning placeholder results. That behavior
is a code-audit requirement even if no additional Phase 38 todo currently
captures it.
