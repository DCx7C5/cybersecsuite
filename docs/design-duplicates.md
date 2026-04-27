---
title: Design Decision - Intentional Duplicates
date: 2024-04-27
status: approved
author: CyberSecSuite Team
---

# Design Decision: Intentional Duplicates in CyberSecSuite

## Overview

This document explains which data structures and models intentionally allow duplicate entries and why they are designed this way.

## Intentional Duplicates

### 1. CVE Intelligence Entry History

**Model:** `src/db/models/cve_entry.py::CVEIntelligenceEntry`

**Rationale:**
- CVE entries track intelligence history from multiple sources over time
- The same CVE identifier can appear multiple times with different:
  - Timestamps (when intelligence was updated)
  - Sources (different intelligence feeds)
  - Scores (CVSS scores may be updated)
  - Descriptions (threat context evolves)
- Duplicates preserve audit trail and allow tracking how threat assessment changed

**Design Pattern:**
```python
class CVEIntelligenceEntry(Model):
    """Line/item entries from cve-intelligence.md (history can include duplicates)."""
    cve_identifier = fields.CharField(max_length=32)  # Not unique
    published_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)
    # Multiple entries for same CVE allowed
```

**Query Pattern:** Get latest entry for a CVE:
```python
entry = await CVEIntelligenceEntry.filter(cve_identifier='CVE-2024-1234').order_by('-published_at').first()
```

---

### 2. Feed Snapshot Records

**Model:** `src/db/models/feed_snapshot.py::ThreatIntelFeedSnapshot`

**Rationale:**
- Multiple threat intelligence feeds can report the same indicator (IOC)
- Duplicates across feeds show:
  - Consensus (indicator reported by multiple trusted sources)
  - Source reliability (how many feeds independently detected it)
  - First discovery time (earliest appearance in any feed)
- Maintains provenance for incident response ("which feed warned us first?")

**Deduplication Handling:**
- Application layer deduplicates by IOC value when aggregating for presentation
- Raw duplicates preserved in database for audit/replay capability
- See: `utils/deduplication.py::deduplicate_items()`

---

### 3. MISP Event Attributes

**Model:** `src/db/models/misp.py::MISPAttributeIntel`

**Rationale:**
- MISP events can have duplicate attributes (e.g., same hash, domain listed twice)
- Duplicates in MISP represent:
  - Multiple analysts discovering same artifact
  - Reference tracking (same IOC appearing in multiple contexts)
  - Event enrichment history
- Deduplication happens during bootstrap parsing to normalize data

**See:**
- `src/db/intel/_loaders.py::_extract_misp_attributes()`
- `src/db/intel/_utils.py::_dedupe_strings()` - consolidates tags after extraction

---

### 4. OpenCTI Indicator Types & Labels

**Models:** `src/db/models/opencti.py::OpenCTIIndicatorIntel`, `OpenCTIEntityIntel`

**Rationale:**
- OpenCTI can assign same indicator type/label multiple times
- During bootstrap loading, we intentionally:
  - Extract all labels including duplicates
  - Deduplicate them using `deduplicate_strings()` for normalized storage
  - Preserve count information for "popularity" metrics

**See:**
- `src/db/intel/bootstrap.py` - uses `_dedupe_strings()` for tags, motivations, sectors

---

### 5. Worker Context - Task Deduplication

**Module:** `src/db/models/worker_context.py`

**Rationale:**
- Workers may receive same task from different sources
- Task deduplication prevents duplicate processing while maintaining:
  - Source traceability
  - Execution time tracking
  - Worker load balancing insights

**Design:** See context_awareness module for intelligent routing

---

## Deduplication Patterns (Consolidated)

See: `src/utils/deduplication.py`

### When Deduplication Happens

| Pattern | Location | Use Case |
|---------|----------|----------|
| `deduplicate_strings()` | intel bootstrap | Normalize tags, labels, sectors |
| `deduplicate_items()` | feed parsing | Preserve order while removing duplicates |
| `deduplicate_messages()` | AI context compression | Remove similar consecutive messages |
| `deduplicate_by_key()` | Available for custom logic | Dedup by field value |

### When Deduplication Does NOT Happen

- **CVE history** - Keep all entries for audit trail
- **Feed snapshots** - Keep per-source entries for provenance
- **MISP attributes** - Keep raw data, deduplicate at query layer if needed

---

## Implementation Notes

### For Developers

1. **Adding new duplicate-friendly data:**
   - Document in this file why duplicates are needed
   - Use indexing to support efficient queries (e.g., `.order_by('-published_at')`)
   - Consider denormalizing "latest" snapshot for performance

2. **Adding new deduplication logic:**
   - Add function to `src/utils/deduplication.py`
   - Document original location and use case
   - Update imports to use consolidated utilities

3. **Querying duplicate-rich tables:**
   ```python
   # Get latest per group (e.g., latest CVE entry per identifier)
   from tortoise.functions import F
   from tortoise import QuerySet
   
   latest = await CVEIntelligenceEntry.raw("""
       SELECT DISTINCT ON (cve_identifier) * 
       FROM intel_cve_entries 
       ORDER BY cve_identifier, published_at DESC
   """)
   ```

---

## Migration & Cleanup

### If removing duplicates becomes necessary:

1. Create dated backup snapshot
2. Run one-time cleanup script (add to `src/manage/cleanup.py`)
3. Update indexes and queries
4. Document in migration notes

---

## Related Files

- `src/utils/deduplication.py` - Consolidated deduplication functions
- `src/db/intel/_utils.py` - Intel-specific helpers using deduplication
- `src/db/intel/_loaders.py` - Feed parsing with deduplication
- `src/ai_proxy/validation/json_response.py` - Message deduplication for context

---

## Approval

- [ ] Architecture Team
- [ ] Database Team
- [ ] Security Review
- [x] Documentation

**Last Updated:** 2024-04-27
