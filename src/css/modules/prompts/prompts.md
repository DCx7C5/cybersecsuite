# @prompts — Prompt Registry & Template Engine

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

## Purpose

The `@prompts` module manages **prompts as first-class entities** — reusable, versioned, tagged text templates with variable substitution. This is **not MCP prompts**. This is the platform's own prompt library.

Prompts are:
- **Stored** in the database (versioned, taggable, searchable)
- **Parameterized** via `{{variable}}` placeholders with typed schemas
- **Rendered** at execution time (variables resolved, provider format applied)
- **Catalogued** in the marketplace (`MarketplaceItemType.prompt` already exists)
- **Composed** — prompts can include other prompts via `{{> partial_id}}`

---

## Scope

| In scope | Out of scope |
|----------|-------------|
| PromptDefinition storage + versioning | MCP protocol prompts (unrelated) |
| Template variable substitution | Provider-side prompt caching (Phase 11) |
| Prompt categories (system/user/few-shot/chain) | Agent execution (agents/ uses prompts, doesn't own them) |
| Marketplace integration | Anthropic prompt library API (external) |
| FastAPI CRUD endpoints | Jinja2 dependency (use simple regex renderer) |

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.marketplace` | ← catalogues | `MarketplaceItemType.prompt` items point to PromptDefinition |
| `css.modules.agents` | → consumes | Agents resolve prompt IDs → rendered strings at runtime |
| `css.modules.tags` | → consumes | Prompts are taggable (tags module manages tag entities) |
| `css.core.types.query` | → feeds | `Query.prompt` field populated from rendered PromptDefinition |
| `css.core.db` | → persists to | Tortoise ORM PromptDefinition model |

---

## Module Files (Target)

```
prompts/
├── __init__.py        ← exports PromptRegistry, get_prompt_registry, PromptDefinition
├── enums.py           ← PromptCategory, PromptStatus, PromptVariableType
├── exceptions.py      ← PromptNotFoundError, PromptRenderError, PromptValidationError
├── types.py           ← PromptVariable, PromptVersion, PromptRenderResult (msgspec.Struct)
├── registry.py        ← PromptRegistry singleton — CRUD + render + search
├── renderer.py        ← PromptRenderer — {{var}} substitution + {{> partial}} includes
├── models.py          ← Tortoise ORM: PromptDefinition, PromptVersion (DB persistence)
├── endpoints.py       ← FastAPI: /api/prompts/* (CRUD + render + search)
└── prompts.md         ← this file
```

---

## Key Types

### PromptCategory (enum)

```python
class PromptCategory(str, Enum):
    SYSTEM        = "system"       # System message / role context
    USER          = "user"         # User-turn templates
    FEW_SHOT      = "few_shot"     # Example pairs (input/output)
    CHAIN         = "chain"        # Multi-step chain prompts
    PERSONA       = "persona"      # Character / role definitions
    INSTRUCTION   = "instruction"  # Task instructions
    CUSTOM        = "custom"
```

### PromptVariable (msgspec.Struct, frozen)

```python
class PromptVariable(msgspec.Struct, frozen=True):
    name: str                        # {{variable_name}}
    var_type: PromptVariableType     # STRING, INT, BOOL, LIST, PROMPT_REF
    description: str = ""
    required: bool = True
    default: str | None = None
```

### PromptDefinition (msgspec.Struct, frozen)

```python
class PromptDefinition(msgspec.Struct, frozen=True):
    prompt_id: str                   # slug: "sec-audit-system-v2"
    name: str
    description: str
    category: PromptCategory
    content: str                     # Raw template with {{vars}} and {{> partials}}
    variables: list[PromptVariable]
    version: str = "1.0.0"
    status: PromptStatus = PromptStatus.ACTIVE
    tags: list[str] = []
    author: str = ""
    language: str = "en"
```

### PromptRenderResult (msgspec.Struct, frozen)

```python
class PromptRenderResult(msgspec.Struct, frozen=True):
    prompt_id: str
    rendered: str                    # Final text after variable substitution
    variables_used: dict[str, str]   # What was substituted
    missing_variables: list[str]     # Required vars not provided (error if any)
    partial_ids_used: list[str]      # {{> partial}} IDs resolved
```

---

## PromptRegistry API

```python
registry = get_prompt_registry()

# Register a prompt
registry.register(PromptDefinition(
    prompt_id="sec-audit-system",
    name="Security Audit System Prompt",
    category=PromptCategory.SYSTEM,
    content="You are a senior security engineer conducting a {{audit_type}} audit on {{target}}.",
    variables=[
        PromptVariable(name="audit_type", var_type=PromptVariableType.STRING),
        PromptVariable(name="target", var_type=PromptVariableType.STRING),
    ],
    tags=["security", "audit", "system"],
))

# Render at runtime
result = registry.render("sec-audit-system", audit_type="penetration", target="web API")
# result.rendered == "You are a senior security engineer conducting a penetration audit on web API."

# Search
prompts = registry.search(category=PromptCategory.SYSTEM, tags=["security"])

# Versioned lookup
registry.get("sec-audit-system", version="1.0.0")
```

---

## Renderer Rules

- Variables: `{{variable_name}}` — replaced by string value
- Partials: `{{> prompt_id}}` — replaced by resolved content of another prompt (non-recursive, one level)
- Missing required vars → `PromptRenderError` with list of missing names
- Missing optional vars → substituted with empty string or default value
- Renderer is pure Python (no Jinja2 dep) — simple regex replace

---

## Phase 23 Todos

| Todo ID | Description | Task |
|---------|-------------|------|
| `prompt-enums` | PromptCategory + PromptStatus + PromptVariableType | T23.1-foundation |
| `prompt-exceptions` | PromptNotFoundError, PromptRenderError, PromptValidationError | T23.1-foundation |
| `prompt-types-struct` | PromptVariable + PromptDefinition + PromptRenderResult | T23.1-foundation |
| `prompt-registry` | PromptRegistry singleton (CRUD + search + version) | T23.2-registry |
| `prompt-renderer` | PromptRenderer: {{var}} substitution + {{> partial}} includes | T23.2-registry |
| `prompt-models` | Tortoise ORM PromptDefinition + PromptVersionRecord | T23.3-persistence |
| `prompt-endpoints` | FastAPI /api/prompts/* (CRUD + render + search) | T23.4-api |
| `prompt-marketplace-wire` | Link PromptDefinition ↔ MarketplaceItemType.prompt | T23.5-integration |
| `prompt-module-plan` | Write prompts/prompts.md (this file — DONE) | T23.0-docs |
| `prompt-rules-update` | Add prompts to rules.md modules table (21 modules) | T23.0-docs |

---

## Rules

- msgspec.Struct (frozen) for all value types — NOT dataclass
- No Jinja2 dependency — simple regex renderer
- `Protocol` not ABC for renderer interface
- Loader.py auto-discovers `endpoints.py` and `models.py`
- All async methods where DB is involved

---

## 🔄 Sync Reminder

> **BIDIRECTIONAL SYNC REQUIRED**: This file and `.plan/session.db` must always be in sync.  
> Phase 23 — Prompt Registry | 10 todos | All pending as of 2026-05-04
