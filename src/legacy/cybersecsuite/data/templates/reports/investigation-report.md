# Investigation Report — {{CASE_ID}}

## Executive Summary
| Field                    | Value                         |
|--------------------------|-------------------------------|
| **Case ID**              | {{CASE_ID}}                   |
| **Project Name**         | {{PROJECT_NAME}}              |
| **Classification**       | {{CLASSIFICATION}}            |
| **Incident Type**        | {{INCIDENT_TYPE}}             |
| **Overall Severity**     | {{SEVERITY}}                  |
| **Status**               | {{STATUS}}                    |
| **Investigation Period** | {{START_DATE}} — {{END_DATE}} |
| **Sessions Conducted**   | {{SESSION_COUNT}}             |
| **Lead Investigator**    | {{LEAD_INVESTIGATOR}}         |
| **Verdict**              | {{VERDICT}}                   |
| **Verdict Confidence**   | {{VERDICT_CONFIDENCE}}        |
| **Attribution Confidence** | {{ATTRIBUTION_CONFIDENCE}}  |

## Key Findings
{{KEY_FINDINGS}}

## Project Scope Notes
{{SCOPE_NOTES}}

---

## Technical Analysis

### Target System
| Property     | Value                                |
|--------------|--------------------------------------|
| OS           | {{OS}} {{DISTRIBUTION}}              |
| Kernel       | {{KERNEL}}                           |
| Architecture | {{ARCHITECTURE}}                     |
| Hostname     | {{HOSTNAME}}                         |
| Desktop      | {{DESKTOP_ENV}}                      |
| GPU          | {{GPU_INFO}}                         |
| Network      | {{NETWORK_INTERFACE}} @ {{LOCAL_IP}} |

### Attack Vector Analysis
{{ATTACK_VECTOR_ANALYSIS}}

### Kill Chain Reconstruction
| Phase | Observed Activity | Evidence | Confidence |
|-------|-------------------|----------|------------|
{{KILL_CHAIN}}

### IOC Summary
| Category        | Count                     | Critical | High | Medium | Low |
|-----------------|---------------------------|----------|------|--------|-----|
| Network         | {{NETWORK_IOC_COUNT}}     |          |      |        |     |
| File            | {{FILE_IOC_COUNT}}        |          |      |        |     |
| Process         | {{PROCESS_IOC_COUNT}}     |          |      |        |     |
| Persistence     | {{PERSISTENCE_IOC_COUNT}} |          |      |        |     |
| eBPF            | {{EBPF_IOC_COUNT}}        |          |      |        |     |
| Memory          | {{MEMORY_IOC_COUNT}}      |          |      |        |     |
| Firmware / Boot | {{FIRMWARE_IOC_COUNT}}    |          |      |        |     |
| Log / Event     | {{LOG_IOC_COUNT}}         |          |      |        |     |
| Credential      | {{CREDENTIAL_IOC_COUNT}}  |          |      |        |     |
| **Total**       | **{{IOC_COUNT}}**         |          |      |        |     |

### MITRE ATT&CK Mapping
| Technique ID | Technique Name | Tactic | IOC Ref | Evidence Summary |
|--------------|----------------|--------|---------|------------------|
{{MITRE_MAPPING}}

---

## Investigation Timeline
{{TIMELINE}}

## Evidence Chain of Custody
| Artifact | Source | SHA-256 | Collected | Session | Storage Path |
|----------|--------|---------|-----------|---------|--------------|
{{EVIDENCE_CHAIN}}

## Risk Assessment
| Risk | Impact | Likelihood | Current Mitigation | Residual Risk |
|------|--------|------------|--------------------|---------------|
{{RISK_ASSESSMENT}}

---

## Recommendations

### Immediate Actions (within 24h)
{{IMMEDIATE_ACTIONS}}

### Short-term Mitigations (within 1 week)
{{SHORT_TERM_MITIGATIONS}}

### Long-term Mitigations (within 1 month)
{{LONG_TERM_MITIGATIONS}}

---

## Conclusion
{{CONCLUSION}}

## Lessons Learned
{{LESSONS_LEARNED}}

## Appendices
- **A:** Full IOC list → `ioc-db.md`
- **B:** Session logs → `cybersec-sessions/`
- **C:** Raw artefacts → `$SESSION_DIR/artefacts/`
- **D:** PCAP files → `$SESSION_DIR/raw_dumps/`
{{ADDITIONAL_APPENDICES}}
