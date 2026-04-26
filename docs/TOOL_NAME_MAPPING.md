# Tool Name Mapping Document

**Status:** Pre-Phase-1 Planning  
**Purpose:** Establish tool name migration strategy for MCP externalization  
**Last Updated:** 2026-04-26  
**Target Phase:** Phase 1-2 (extraction), Phase 8 (skill migration)

---

## 1. Problem Statement

### Current State
The CyberSecSuite implements 87 security tools within a monolithic MCP server (`mcp__cybersec__*`). These tools follow a naming convention:

```
mcp__cybersec__add_finding
mcp__cybersec__add_ioc
mcp__cybersec__suggest_mitre
mcp__cybersec__get_project_memory
mcp__cybersec__add_case
...
```

### Post-Extraction State
When MCP extraction completes (Phases 1-7), tools will be distributed across 12 specialized MCPs:

```
mcp__incident_management__add_finding
mcp__threat_intelligence__add_ioc
mcp__threat_intelligence__suggest_mitre
mcp__incident_management__get_case
...
```

### Impact
- **799 SKILL.md files** reference current tool names (`mcp__cybersec__*`)
- **Phase 8 migration** must rewrite all skill references to new names
- **Without mapping:** Skills become broken references → tools fail to execute
- **With mapping:** Automated migration ensures 100% correctness

---

## 2. Migration Strategy (3 Phases)

### Phase 1-2: MCP Extraction & Tool Creation
**Responsibility:** Specialized agents (one per MCP)

- Extract tool implementations from monolithic server
- Create new MCP modules with extracted tools
- **Tool naming convention:** `mcp__{mcp_name}__{function_name}`
- Generate tool definitions in new MCPs with auto-incremented names
- Record all mappings in `tools_migration_manifest.json`

**Output:** 
- 12 new MCP packages
- Each with `tools_migration_manifest.json` containing:
  ```json
  {
    "mcp_name": "incident_management",
    "tools": [
      {"old_name": "mcp__cybersec__add_finding", "new_name": "mcp__incident_management__add_finding", "function": "add_finding", "phase": 3},
      {"old_name": "mcp__cybersec__get_case", "new_name": "mcp__incident_management__get_case", "function": "get_case", "phase": 3}
    ]
  }
  ```

### Phase 8: Skill Reference Migration
**Responsibility:** Unified tool mapping rewrite

1. **Aggregate mappings:** Collect all 12 `tools_migration_manifest.json` files
2. **Merge manifests:** Create master `TOOL_NAME_MAPPING_COMPLETE.json`
3. **Validate mappings:** Verify no collisions, all tools exist
4. **Rewrite skills:** Use mapping to update all 799 SKILL.md files
5. **Verification:** Scan for orphaned old names, validate new names against installed MCPs

**Output:**
- Master mapping file (CSV + JSON formats)
- Updated 799 SKILL.md files
- Migration report (success rate, errors, orphans)

### Phase 9: Deployment & Validation
- Install all 12 MCPs respecting dependency order
- Test 100 random skills → verify tool references work
- Monitor agent logs for missing tool errors
- Rollback plan: maintain old mapping for fallback

---

## 3. Full Mapping Table (Template + Examples)

### Legend
| Column | Meaning |
|--------|---------|
| old_name | Current tool name in monolithic cybersec MCP |
| new_name | Tool name in extracted MCP |
| mcp_name | Target MCP after extraction |
| function | Python function name |
| phase | Extraction phase (2-7) |
| category | Tool category for validation |

### Incident Management MCP (Phase 3 Extraction)

| old_name | new_name | mcp_name | function | phase | category |
|----------|----------|----------|----------|-------|----------|
| mcp__cybersec__add_finding | mcp__incident_management__add_finding | incident_management | add_finding | 3 | findings |
| mcp__cybersec__get_recent_findings | mcp__incident_management__get_recent_findings | incident_management | get_recent_findings | 3 | findings |
| mcp__cybersec__update_finding | mcp__incident_management__update_finding | incident_management | update_finding | 3 | findings |
| mcp__cybersec__add_case | mcp__incident_management__add_case | incident_management | add_case | 3 | cases |
| mcp__cybersec__get_case | mcp__incident_management__get_case | incident_management | get_case | 3 | cases |
| mcp__cybersec__list_cases | mcp__incident_management__list_cases | incident_management | list_cases | 3 | cases |
| mcp__cybersec__close_case | mcp__incident_management__close_case | incident_management | close_case | 3 | cases |

### Threat Intelligence MCP (Phase 2 Extraction)

| old_name | new_name | mcp_name | function | phase | category |
|----------|----------|----------|----------|-------|----------|
| mcp__cybersec__add_ioc | mcp__threat_intelligence__add_ioc | threat_intelligence | add_ioc | 2 | iocs |
| mcp__cybersec__query_ioc | mcp__threat_intelligence__query_ioc | threat_intelligence | query_ioc | 2 | iocs |
| mcp__cybersec__correlate_iocs | mcp__threat_intelligence__correlate_iocs | threat_intelligence | correlate_iocs | 2 | iocs |
| mcp__cybersec__suggest_mitre | mcp__threat_intelligence__suggest_mitre | threat_intelligence | suggest_mitre | 2 | mitre |
| mcp__cybersec__lookup_cve | mcp__threat_intelligence__lookup_cve | threat_intelligence | lookup_cve | 2 | vulnerabilities |
| mcp__cybersec__lookup_cwe | mcp__threat_intelligence__lookup_cwe | threat_intelligence | lookup_cwe | 2 | vulnerabilities |

### Forensic Vault MCP (Phase 2 Extraction)

| old_name | new_name | mcp_name | function | phase | category |
|----------|----------|----------|----------|-------|----------|
| mcp__cybersec__get_project_memory | mcp__forensic_vault__get_project_memory | forensic_vault | get_project_memory | 2 | memory |
| mcp__cybersec__vault_ingest | mcp__forensic_vault__vault_ingest | forensic_vault | vault_ingest | 2 | vault |
| mcp__cybersec__vault_query | mcp__forensic_vault__vault_query | forensic_vault | vault_query | 2 | vault |
| mcp__cybersec__vault_lint | mcp__forensic_vault__vault_lint | forensic_vault | vault_lint | 2 | vault |

### Network Layers MCP (Phase 4 Extraction)

| old_name | new_name | mcp_name | function | phase | category |
|----------|----------|----------|----------|-------|----------|
| mcp__cybersec__map_network | mcp__network_layers__map_network | network_layers | map_network | 4 | network |
| mcp__cybersec__analyze_traffic | mcp__network_layers__analyze_traffic | network_layers | analyze_traffic | 4 | network |
| mcp__cybersec__decode_packet | mcp__network_layers__decode_packet | network_layers | decode_packet | 4 | network |

### Session Management MCP (Phase 4 Extraction)

| old_name | new_name | mcp_name | function | phase | category |
|----------|----------|----------|----------|-------|----------|
| mcp__cybersec__create_session | mcp__session_management__create_session | session_management | create_session | 4 | sessions |
| mcp__cybersec__get_session | mcp__session_management__get_session | session_management | get_session | 4 | sessions |
| mcp__cybersec__list_sessions | mcp__session_management__list_sessions | session_management | list_sessions | 4 | sessions |

### Advanced Analysis MCP (Phase 5 Extraction)

| old_name | new_name | mcp_name | function | phase | category |
|----------|----------|----------|----------|-------|----------|
| mcp__cybersec__ml_threat_score | mcp__advanced_analysis__ml_threat_score | advanced_analysis | ml_threat_score | 5 | ml |
| mcp__cybersec__correlate_events | mcp__advanced_analysis__correlate_events | advanced_analysis | correlate_events | 5 | analysis |
| mcp__cybersec__timeline_reconstruct | mcp__advanced_analysis__timeline_reconstruct | advanced_analysis | timeline_reconstruct | 5 | analysis |

### Browser Automation MCP (Phase 5 Extraction)

| old_name | new_name | mcp_name | function | phase | category |
|----------|----------|----------|----------|-------|----------|
| mcp__cybersec__screenshot | mcp__browser_automation__screenshot | browser_automation | screenshot | 5 | browser |
| mcp__cybersec__navigate_to | mcp__browser_automation__navigate_to | browser_automation | navigate_to | 5 | browser |
| mcp__cybersec__click_element | mcp__browser_automation__click_element | browser_automation | click_element | 5 | browser |

### Utility Tools MCP (Phase 6 Extraction)

| old_name | new_name | mcp_name | function | phase | category |
|----------|----------|----------|----------|-------|----------|
| mcp__cybersec__crypto_sign | mcp__utility_tools__crypto_sign | utility_tools | crypto_sign | 6 | crypto |
| mcp__cybersec__crypto_verify | mcp__utility_tools__crypto_verify | utility_tools | crypto_verify | 6 | crypto |
| mcp__cybersec__json_format | mcp__utility_tools__json_format | utility_tools | json_format | 6 | formatting |

### Business Tools MCP (Phase 6 Extraction)

| old_name | new_name | mcp_name | function | phase | category |
|----------|----------|----------|----------|-------|----------|
| mcp__cybersec__generate_report | mcp__business_tools__generate_report | business_tools | generate_report | 6 | reporting |
| mcp__cybersec__export_findings | mcp__business_tools__export_findings | business_tools | export_findings | 6 | reporting |

### Database Tools MCP (Phase 2 Extraction - Foundation)

| old_name | new_name | mcp_name | function | phase | category |
|----------|----------|----------|----------|-------|----------|
| mcp__cybersec__query_db | mcp__database_tools__query_db | database_tools | query_db | 2 | database |
| mcp__cybersec__write_entry | mcp__database_tools__write_entry | database_tools | write_entry | 2 | database |

**Note:** Complete mapping contains ~99 total entries (20+ examples shown above). Full mapping auto-generated in Phase 2 via `scripts/generate_tool_mapping.py`.

---

## 4. Mapping Principles

### Naming Convention
All extracted tools follow the pattern:
```
mcp__{mcp_name}__{function_name}
```

**Rules:**
1. `mcp_name`: Lowercase, hyphen-separated MCP identifier
2. `function_name`: Lowercase, underscore-separated Python function name
3. Total length: < 80 characters
4. No collisions: each tool name globally unique across all MCPs

**Examples:**
```
mcp__threat_intelligence__suggest_mitre        ✅ Valid
mcp__incident_management__add_finding          ✅ Valid
mcp__database_tools__write_entry               ✅ Valid
mcp__cybersec__old_tool_name                   ❌ Invalid (old namespace)
mcp__threat_intel__suggest_mitre               ❌ Invalid (truncated name)
mcp__threat_intelligence_suggest_mitre         ❌ Invalid (wrong separator)
```

### Consistency Rules
- All tools in same MCP share `mcp__{mcp_name}__` prefix
- Tool names don't change after extraction (immutable post-Phase 2)
- Function names remain unchanged from source code
- No tool name abbreviations (clarity over brevity)

### Collision Avoidance
- Phase 2 CI/CD validates no name collisions
- Global registry tracks all tool names across MCPs
- Automated test: `tools_name_uniqueness_test.py` runs on each extraction

---

## 5. Phase 8 Implementation

### Overview
Phase 8 rewrites all 799 SKILL.md files to reference new tool names using the mapping generated in Phases 1-7.

### Algorithm
```python
# Phase 8: Skill reference migration

def migrate_skill_references():
    # 1. Load master mapping
    mapping = load_tool_mapping('TOOL_NAME_MAPPING_COMPLETE.json')
    old_to_new = {entry['old_name']: entry['new_name'] for entry in mapping}
    
    # 2. Find all SKILL.md files
    skill_files = glob.glob('**/*.SKILL.md', recursive=True)  # ~799 files
    
    for skill_file in skill_files:
        content = read_file(skill_file)
        modified = False
        
        # 3. For each old tool name, replace with new name
        for old_name, new_name in old_to_new.items():
            if old_name in content:
                content = content.replace(old_name, new_name)
                modified = True
                log(f"Replaced {old_name} → {new_name} in {skill_file}")
        
        # 4. Verify all new names are valid
        for new_name in re.findall(r'mcp__\w+__\w+', content):
            if new_name not in installed_tools:
                error(f"Invalid tool reference {new_name} in {skill_file}")
                modified = False
        
        # 5. Write back if modified
        if modified:
            write_file(skill_file, content)
            register_migration(skill_file, old_names, new_names)
    
    return migration_report

def migration_report():
    return {
        'total_skills': 799,
        'migrated': count_modified_skills,
        'errors': count_errors,
        'orphans': count_unmatched_old_names,
    }
```

### Validation Checklist
- ✅ 100% of skills have valid tool references
- ✅ No old `mcp__cybersec__*` names remain
- ✅ All new names exist in installed MCPs
- ✅ Tool signatures match expected inputs
- ✅ Migration report generated (success rate, errors)

### Rollback Strategy
- Maintain git branch with old mappings
- Keep `tools_migration_manifest.json` from each Phase 2-7 extraction
- If Phase 9 deployment fails: revert mappings, redeploy old MCP
- Estimated rollback time: < 30 minutes

---

## 6. Automation Strategy

### Phase 2 Early: Generate Master Mapping
**File:** `scripts/generate_tool_mapping.py`

**Execution:**
```bash
python scripts/generate_tool_mapping.py \
  --input-mcps ./mcp_extracted/ \
  --output-mapping ./docs/TOOL_NAME_MAPPING_COMPLETE.json \
  --format csv,json \
  --validate
```

**Inputs:**
- 12 extracted MCP directories (Phases 1-7)
- Each containing `tools_migration_manifest.json`

**Process:**
1. Scan all MCPs for tool definitions
2. Extract old→new mappings from manifests
3. Validate no collisions, consistent naming
4. Auto-generate mapping in CSV + JSON formats

**Output:**
```csv
old_tool,new_tool,mcp,function,phase,category
mcp__cybersec__add_finding,mcp__incident_management__add_finding,incident_management,add_finding,3,findings
mcp__cybersec__add_ioc,mcp__threat_intelligence__add_ioc,threat_intelligence,add_ioc,2,iocs
...
```

### Phase 8 Later: Migrate Skill References
**File:** `scripts/migrate_skill_references.py`

**Execution:**
```bash
python scripts/migrate_skill_references.py \
  --mapping ./docs/TOOL_NAME_MAPPING_COMPLETE.json \
  --skills-dir ./skills/ \
  --dry-run false \
  --report ./migration_report.json
```

**Inputs:**
- Master mapping (`TOOL_NAME_MAPPING_COMPLETE.json`)
- All SKILL.md files (799 total)
- Installed MCPs for validation

**Process:**
1. Load all skill files
2. For each old tool name, replace with new name
3. Validate new names exist in MCPs
4. Generate migration report
5. Commit changes with migration summary

**Output:**
- Updated 799 SKILL.md files
- Migration report (success/error counts)
- Commit message:
  ```
  chore: migrate tool references to extracted MCPs (Phase 8)
  
  - Updated 799 skills to use new MCP tool namespaces
  - Replaced mcp__cybersec__* with mcp__{mcp}__* references
  - Validation: 100% tool name success rate
  - Migration report: migration_report.json
  
  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
  ```

---

## 7. Validation Strategy

### Phase 2-7: Per-MCP Validation
Each extraction phase validates tool names before committing:

**Checks:**
1. ✅ No `mcp__cybersec__` names remain in new MCP
2. ✅ All tools named `mcp__{mcp_name}__*`
3. ✅ No name collisions within MCP
4. ✅ Python function names match declaration
5. ✅ Tool schemas are valid JSON

**CI/CD Gate:**
```yaml
tool-naming-validation:
  - name: Check tool naming compliance
    run: pytest tests/test_tool_naming.py -v
    must_pass: true
```

### Phase 8: Skill Migration Validation

**Pre-migration checks:**
```bash
# 1. Validate all old names are in mapping
python -c "
mapping = load('TOOL_NAME_MAPPING_COMPLETE.json')
skills = find_all_skills()
old_names = extract_tool_refs(skills)
missing = set(old_names) - set(m['old_name'] for m in mapping)
assert not missing, f'Missing mappings: {missing}'
"

# 2. Validate all new names exist
python -c "
mapping = load('TOOL_NAME_MAPPING_COMPLETE.json')
installed_mcps = get_installed_mcps()
installed_tools = {t for mcp in installed_mcps.values() for t in mcp.tools}
new_names = set(m['new_name'] for m in mapping)
missing = new_names - installed_tools
assert not missing, f'Missing tools: {missing}'
"

# 3. Dry-run migration
python scripts/migrate_skill_references.py --dry-run true
```

**Post-migration checks:**
```bash
# 1. No old names remain
grep -r "mcp__cybersec__" skills/ && exit 1 || echo "✅ No old names"

# 2. All new names are valid
python -c "
skills = find_all_skills()
new_names = extract_tool_refs(skills)
installed = get_installed_tools()
missing = set(new_names) - installed
assert not missing, f'Invalid tool refs: {missing}'
"

# 3. Sample skill test (10 random skills)
python tests/test_skill_tool_references.py -sample 10 -validate
```

### Validation Report
**Output:** `migration_validation_report.json`

```json
{
  "total_skills": 799,
  "migrated": 799,
  "errors": 0,
  "warnings": 0,
  "orphans": 0,
  "tool_coverage": "100%",
  "pre_migration_checks": {
    "mapping_completeness": "PASS",
    "tool_existence": "PASS",
    "dry_run": "PASS"
  },
  "post_migration_checks": {
    "old_names_remaining": 0,
    "new_names_valid": "PASS",
    "tool_accessibility": "PASS"
  },
  "timestamp": "2026-XX-XX",
  "duration_minutes": 45
}
```

---

## 8. Risk Analysis & Mitigation

### Risk: Tool Name Mapping Incorrect
**Impact:** Skills execute wrong tools or fail  
**Probability:** Low (Phase 2 generates + Phase 8 validates)  
**Mitigation:**
- Auto-generate mapping from source code (deterministic)
- Validate before/after in CI/CD
- Dry-run Phase 8 migration before committing
- Maintain old MCP fallback until Phase 9 validation

### Risk: Incomplete Migration
**Impact:** Some skills reference old names → broken  
**Probability:** Medium (799 files × many refs each)  
**Mitigation:**
- Automated migration script (not manual)
- Final grep check for old names
- Per-MCP tool count validation
- Rollback plan ready

### Risk: MCP Tool Count Mismatch
**Impact:** Mapping has tools that don't exist in MCPs  
**Probability:** Low (Phase 2 creates mappings from MCPs)  
**Mitigation:**
- Phase 8 validates all new names against installed MCPs
- Fail if validation doesn't reach 100%
- Report any missing tools immediately

---

## 9. Integration with Phase Execution

### Phase 1: Planning & Analysis
- Create this document ✅
- Analyze current tool names
- Design extraction order
- Identify dependencies

### Phase 2: Foundation MCP Extraction
- Extract `database-tools` MCP
- Generate `tools_migration_manifest.json`
- Example mapping: database queries
- CI/CD validates tool naming

### Phase 3-7: Specialized MCP Extraction
- Each phase generates tool mappings
- Aggregate mappings in master file
- Validate no collisions between phases
- Maintain consistency across MCPs

### Phase 8: Skill Reference Migration
- Load master mapping
- Rewrite 799 SKILL.md files
- Validate 100% success
- Generate migration report

### Phase 9: Deployment
- Install all 12 MCPs respecting dependencies
- Verify tool references work in live system
- Monitor for missing tool errors
- Rollback if needed (< 30 min)

---

## 10. Examples & Runbooks

### Example: Migrate Single Skill
```bash
# 1. View current tool references
grep -o "mcp__[^\"]*" skillz/incident_response.SKILL.md

# Output:
# mcp__cybersec__add_finding
# mcp__cybersec__add_ioc
# mcp__cybersec__get_case

# 2. Apply mapping manually (or via script)
sed -i 's/mcp__cybersec__add_finding/mcp__incident_management__add_finding/g' \
  skillz/incident_response.SKILL.md
sed -i 's/mcp__cybersec__add_ioc/mcp__threat_intelligence__add_ioc/g' \
  skillz/incident_response.SKILL.md
sed -i 's/mcp__cybersec__get_case/mcp__incident_management__get_case/g' \
  skillz/incident_response.SKILL.md

# 3. Verify new names
grep -o "mcp__[^\"]*" skillz/incident_response.SKILL.md

# Output:
# mcp__incident_management__add_finding ✅
# mcp__threat_intelligence__add_ioc ✅
# mcp__incident_management__get_case ✅
```

### Example: Verify Mapping Correctness
```bash
# Generate all tools from extracted MCPs
python -c "
import json
from pathlib import Path

mapping = {}
for mcp_dir in Path('mcp_extracted').glob('mcp_*'):
    manifest_file = mcp_dir / 'tools_migration_manifest.json'
    if manifest_file.exists():
        with open(manifest_file) as f:
            data = json.load(f)
            for tool in data['tools']:
                old = tool['old_name']
                new = tool['new_name']
                if old in mapping and mapping[old] != new:
                    print(f'COLLISION: {old} → {mapping[old]} vs {new}')
                else:
                    mapping[old] = new

# Output mapping
with open('TOOL_NAME_MAPPING_COMPLETE.json', 'w') as f:
    json.dump([{'old': k, 'new': v} for k, v in mapping.items()], f, indent=2)

print(f'✅ Mapping generated: {len(mapping)} tools')
"
```

---

## 11. Success Criteria

✅ **Mapping completeness:** All 87 tools have old→new mappings  
✅ **No collisions:** Each tool name globally unique  
✅ **Phase order:** Extraction phases ordered by dependencies  
✅ **Skill count:** 100% of 799 skills migrated  
✅ **Validation:** All new tool names exist in installed MCPs  
✅ **Automation:** Scripts ready for Phase 8 execution  
✅ **Documentation:** This document complete and ready for reference  

---

## Appendix A: Tool Category Distribution

| Category           | Count   | MCP                 |
|--------------------|---------|---------------------|
| Findings & Cases   | 10      | incident_management |
| IOCs               | 8       | threat_intelligence |
| Memory & Vault     | 6       | forensic_vault      |
| MITRE/CVE/CWE      | 8       | threat_intelligence |
| Network            | 6       | network_layers      |
| Sessions           | 4       | session_management  |
| ML & Analysis      | 8       | advanced_analysis   |
| Browser Automation | 6       | browser_automation  |
| Crypto & Utility   | 8       | utility_tools       |
| Reporting          | 4       | business_tools      |
| Database           | 6       | database_tools      |
| Other              | 7       | orchestration       |
| **Total**          | **~87** | **12 MCPs**         |

---

## Appendix B: Related Documents

- `docs/MCP_DEPENDENCY_GRAPH.md` — Dependency hierarchy for Phase extraction order
- `scripts/generate_tool_mapping.py` — Auto-generate mapping in Phase 2
- `scripts/migrate_skill_references.py` — Migrate skills in Phase 8
- `tests/test_tool_naming.py` — CI/CD validation for tool names
- `TOOL_NAME_MAPPING_COMPLETE.json` — Master mapping (generated Phase 2)
- `migration_report.json` — Phase 8 execution report
