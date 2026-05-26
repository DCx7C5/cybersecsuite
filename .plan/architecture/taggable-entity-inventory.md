# Phase 40 Lane E - Taggable Entity Inventory (db40-taggable-entity-inventory)

**Tracking authority**: `.plan/session.db` | **Status**: In progress | **Date**: 2026-05-26

---

## Executive Summary

Inventory of models requiring tag-based classification support across the codebase. 
Follows from Lane E scope definition in `src/css/core/db/models/postgres-models.md` (lines 179-199).

This inventory:
- Identifies which ORM models should have M2M tag junction tables
- Confirms existing tag patterns across LLMModel, MarketplaceItem, and HybridToolDefinition
- Catalogs models requiring tag support to enable runtime filtering/discovery/policy

**Owned write surface**: `src/css/modules/tags/*`, `src/css/core/db/models/llm_models.py`, 
`src/css/core/db/models/marketplace.py`, `src/css/modules/tools/models.py`, `src/css/core/tools/models.py`

---

## Existing Tag-Enabled Models

### ✓ Completed: LLMModel (Phase 40 baseline)
- **Location**: `src/css/core/db/models/llm_models.py`
- **Junction model**: `LLMModelTag` (line 355)
- **Fields**: 
  - `llm_model` → ForeignKeyField("models.LLMModel", related_name="tags_m2m")
  - `tag` → ForeignKeyField("models.Tag", related_name="llm_models")
- **Domain value**: `LLMModelTagInfo` (msgspec.Struct)
- **Purpose**: Classify language models by capability (vision, code, chat), provider tier, etc.
- **Status**: ✓ Complete with M2M manager integration

### ✓ Completed: MarketplaceItem (Phase 40 baseline)
- **Location**: `src/css/core/db/models/marketplace.py`
- **Junction model**: `MarketplaceItemTag` (referenced in line 67)
- **Purpose**: Tag marketplace items (skills, agents, workflows, templates) for discovery/filtering
- **Status**: ✓ Complete with filtering and endpoint support
- **Integration**: Routes support tag-based filtering via `?tag=<slug>` parameters

### ✓ Completed: HybridToolDefinition (tools module)
- **Location**: `src/css/modules/tools/models.py`
- **Junction model**: `HybridToolDefinitionTag` (line 85+)
- **Fields**:
  - `hybrid_tool` → ForeignKeyField("models.HybridToolDefinition", related_name="tags_m2m")
  - `tag` → ForeignKeyField("models.Tag", related_name="hybrid_tools")
  - `created_at` → DatetimeField(auto_now_add=True)
- **Constraints**: `unique_together = [("hybrid_tool_id", "tag_id")]` with composite index
- **Purpose**: Classify reusable hybrid tool definitions for discovery
- **Status**: ✓ Complete with M2M and unique constraint

---

## Models Requiring Tag Support (Next Actions)

### 🟡 Pending: SkillDefinitionModel
- **Location**: `src/css/modules/skills/models.py`
- **Current state**: No tag junction defined; only base model exists
- **Model fields**: name, description, category, version, author, enabled, parameters_schema, result_schema, etc.
- **Rationale**: 
  - Skills are discoverable resources like tools and agents
  - Classification tags needed for: difficulty level, use case category (testing, analysis, generation), primary language, data classification (PII sensitivity), certification/approval status
- **Integration points**: 
  - `src/css/modules/skills/endpoints.py` — skill discovery/search endpoints should filter by tag
  - Skill marketplace may surface tags in skill cards
- **Required junction naming**: `SkillDefinitionModelTag` per Phase 40 Lane E naming standard (db40-tag-junction-naming-standard)
- **Action**: Create `SkillDefinitionModelTag` in `src/css/modules/skills/models.py` following HybridToolDefinitionTag pattern

### ❌ Out of Scope: Agent Models (runtime domain value types only)
- **Location**: `src/css/modules/agents/models.py` exists
- **Current state**: Only msgspec.Struct value types (AgentConfig, AgentMessage, AgentMetrics, AgentState, AgentResult, AgentTurn, ConversationContext) — **No ORM backing**
- **Rationale**: Agents are runtime ephemeral; no persistent catalog ORM table for tags to link to
- **Decision**: Defer agent tagging to future phase if agent persistence layer is added
- **Action**: None for Lane E

### ❌ Out of Scope: Workflow Models (no ORM models file)
- **Location**: `src/css/modules/workflows/models.py` — **FILE DOES NOT EXIST**
- **Current state**: No ORM workflow persistence layer
- **Rationale**: Workflows may exist as configuration files or runtime instances, not persistent ORM catalog
- **Decision**: Workflows are out of Lane E scope; defer tagging to future phase if workflow ORM layer is added
- **Action**: None for Lane E

---

## Models Out of Scope for Lane E

The following models are **not candidates** for tag adoption in Lane E (per postgres-models.md scope definition):

### Menu/Navigation Trees
- `MenuItem` (in `menu.py`) — Tagging not applicable; menu is navigation hierarchy, not classification
- `Tag.parent_tag` — Self-reference for taxonomy, not for adoption of BaseTreeModel

### Task/Quota/User/Provider
- `TaskAssignment`, `TaskResult` — Owned by Lane C (task/provider/user); scope boundary
- `TeamQuota` — Owned by Lane C; quota management is not a tagging target
- `User`, `Account`, `Provider` — Identity/authorization models; not tagged entities

### Memory/RAG
- `MemoryEntryRecord`, `MemorySnapshotRecord` — Memory storage is foundational; tagging deferred to retrieval layer

### Infrastructure Models (Machine/Host/PathFS)
- `Machine`, `Host`, `PathFS` — Infrastructure monitoring; tagging would be separate effort in future lane

---

## Tag Classification Categories (Reference)

From `src/css/modules/tags/enums.py` and domain analysis:

### Classification Facets (proposed for Lane E + F)
| Facet | Example values | Applicable to |
|-------|-----------------|---------------|
| **Capability** | vision, code, chat, reasoning, multimodal | LLMModel, SkillDefinitionModel, Agent*, Workflow* |
| **Domain/Use case** | data-pipeline, security, MLOps, research, testing, analysis | Skill*, Workflow*, Agent* |
| **Complexity** | beginner, intermediate, expert | Skill, Workflow, Agent* |
| **Maturity** | experimental, beta, stable, deprecated | LLMModel, Skill*, Workflow*, MarketplaceItem |
| **Certification** | approved, audited, compliance-ready | Skill*, Workflow*, Agent* |
| **Data sensitivity** | public, internal, confidential, pii-handling | Skill*, Workflow*, MarketplaceItem |
| **Language/Framework** | python, typescript, go, bash | Skill*, HybridToolDefinition |
| **Provider/Vendor** | openai, anthropic, google, local | LLMModel |
| **Cost tier** | free, low, medium, high | LLMModel, Skill*, Workflow* |

---

## Implementation Checklist

- [x] Audit existing tag junctions: LLMModelTag, MarketplaceItemTag, HybridToolDefinitionTag ✓
- [x] Confirm Lane E write surface ownership (tools, skills, llm_models, marketplace)
- [ ] Create `SkillDefinitionModelTag` junction in `src/css/modules/skills/models.py`
- [ ] Add `SkillDefinitionModel.tags_m2m` relation property for runtime tag access
- [x] Scan `src/css/modules/{agents,workflows}/` for ORM model presence → Agents has only msgspec types (no ORM), Workflows has no models file
- [x] Agent ORM models: None found (out of scope for Lane E)
- [x] Workflow ORM models: None found (out of scope for Lane E)
- [ ] Document tag category facets in `src/css/modules/tags/tags.md` integration table
- [ ] Validate all junction models follow singular naming convention: `<Model>Tag` (not `<Model>Tags`)

---

## Codebase Scan Results

### Skills Module
- ✓ `SkillDefinitionModel` exists in `src/css/modules/skills/models.py` (line 4+)
- ✓ Skills have description, category, parameters_schema, result_schema
- ✓ Skills are runtime-discoverable entities (skills marketplace list all available)
- ✓ No tag junction currently defined → **Requires `SkillDefinitionModelTag`**

### Agents Module
- ✓ `src/css/modules/agents/models.py` EXISTS
- ✓ Contains: TokenUsage, AgentConfig, AgentMessage, AgentMetrics, AgentState, AgentResult, AgentTurn, ConversationContext
- ✓ **All are msgspec.Struct (runtime domain types), NOT ORM models** → **OUT OF SCOPE for Lane E**
- No Agent ORM persistence layer; agents are ephemeral runtime entities

### Workflows Module
- ✓ `src/css/modules/workflows/models.py` DOES NOT EXIST
- **OUT OF SCOPE for Lane E** — No workflow ORM catalog to tag

---

## Execution Dependencies (Lane E Order)

Lane E child todo order (from postgres-models.md lines 185-190):
1. ✓ `db40-taggable-entity-inventory` — THIS DOCUMENT (in_progress)
2. `db40-tag-junction-naming-standard` — Standardize junction naming (singular `<Model>Tag`)
3. `db40-tag-junction-meta-backfill` — Add Meta/indexes to all junctions
4. `db40-tagging-db-concept` — Define canonical tag category schema
5. `db40-llmmodel-tag-runtime-wire` — Wire tags into runtime queries/filtering

**Blockers for this todo**: None (no dependencies)
**Blockers for next todo** (`db40-tag-junction-naming-standard`): **Completion of this inventory + `SkillDefinitionModelTag` creation**

---

## Next Steps (from this inventory)

1. **Confirm this inventory is complete**:
   - Are SkillDefinitionModel, Agent*, Workflow* the only taggable candidates?
   - Any other ORM models that benefit from classification tags?

2. **Create `SkillDefinitionModelTag` junction**:
   - Add to `src/css/modules/skills/models.py`
   - Follow HybridToolDefinitionTag pattern (FK to model, FK to Tag, unique_together, composite index)
   - Add `SkillDefinitionModelTagInfo` msgspec.Struct value type

3. **Document tagging facets**:
   - Update `src/css/modules/tags/tags.md` integration table with skill/agent/workflow classification examples

4. **Scan agents and workflows modules**:
   - Determine if ORM backing exists; if yes, plan tagging support for next lane iteration

---

**Status**: 🟡 In Progress | **Owner**: Phase 40 Lane E (Tagging consolidation) | **Due**: before `db40-tag-junction-naming-standard`

