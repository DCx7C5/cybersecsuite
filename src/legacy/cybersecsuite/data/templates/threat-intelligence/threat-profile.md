# Threat Actor Profile
> Last updated: {{TIMESTAMP}}  
> Contributing sessions: {{SESSION_LIST}}  
> Confidence in attribution: {{ATTRIBUTION_CONFIDENCE}}

## Structured Profile Entry (`ThreatProfileEntry`)
| Field | Value |
|-------|-------|
| Profile Name | {{PROFILE_NAME}} |
| Linked MITRE Actor | {{ACTOR_NAME or "—"}} |
| Confidence Score | {{CONFIDENCE_SCORE or "—"}} |
| Source File | {{SOURCE_FILE}} |

### Summary
{{THREAT_SUMMARY}}

### Motivations
{{MOTIVATIONS}}

### Target Sectors
{{SECTORS}}

### Target Regions
{{REGIONS}}

### Canonical TTP List
{{TTPS_LIST}}

<!-- One-paragraph high-level assessment: who, what, why, how sophisticated -->

---

## Operational Enrichment (`ThreatProfile` / analyst narrative)

## Known Capabilities
| Capability | Evidence | First Observed | MITRE Technique | Confidence |
|------------|----------|----------------|-----------------|------------|
{{CAPABILITIES}}

## Known Infrastructure
| Type | Value | Context | First Seen | Status | IOC Ref |
|------|-------|---------|------------|--------|---------|
{{INFRASTRUCTURE}}

## Observed TTPs (chronological)
| Date | TTP | MITRE ID | Detail | Session | Confidence |
|------|-----|----------|--------|---------|------------|
{{TTPS}}

## Adversary Tooling
| Tool / Malware | Type | Indicators (hash/name) | Delivery Method | Notes |
|----------------|------|------------------------|-----------------|-------|
{{TOOLING}}

## Communication Patterns
| Pattern | Detail | Frequency | Confidence |
|---------|--------|-----------|------------|
{{COMMUNICATION}}

## Targeting Profile
| Target | Method | Objective | Notes |
|--------|--------|-----------|-------|
{{TARGETING}}
<!-- What does the adversary go after? Cookies, GPU, shell config, etc. -->

## Diamond Model
| Vertex         | Value                      |
|----------------|----------------------------|
| Adversary      | {{ADVERSARY}}              |
| Capability     | {{CAPABILITY_SUMMARY}}     |
| Infrastructure | {{INFRASTRUCTURE_SUMMARY}} |
| Victim         | {{VICTIM_SUMMARY}}         |

## Assessment
{{ASSESSMENT_TEXT}}

## Open Questions
{{OPEN_QUESTIONS}}
<!-- What do we still not know? What should the next session investigate? -->
