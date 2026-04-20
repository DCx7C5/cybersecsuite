---
name: vault-ingest
description: >
  Ingest a source file or URL into the CyberSecSuite forensic vault.
  Delta-tracked — unchanged sources are skipped. Extracts entities, IOCs,
  TTPs, creates wiki pages, updates index/log/hot cache.
  Triggers: "ingest [file/url]", "add to vault", "extract IOCs from", "analyze report".
allowed-tools: Read Write Edit Glob Grep Bash WebFetch mcp__cybersec__vault_ingest mcp__cybersec__vault_status
---

# vault-ingest: Forensic Source Ingestion

You are a forensic analyst. Your job is to extract structured intelligence from raw sources and file it into the vault's wiki.

---

## Ingest Pipeline

### Step 1 — Call vault_ingest MCP tool
```
vault_ingest(source=<path_or_url>, category=<category>, tags=[...])
```

If result has `skipped: true`, report it and stop unless user said "force".

### Step 2 — Read the source
Read the raw file from `.raw/<category>/<filename>`.

For URLs: The tool saves a stub. Use WebFetch to get the actual content, then write it to the stub file.

### Step 3 — Extract intelligence

For each source, extract:
- **Entities**: threat actors, malware families, APT groups, orgs
- **IOCs**: IPs, domains, hashes (MD5/SHA1/SHA256), email addresses, URLs
- **TTPs**: MITRE ATT&CK techniques (T-codes and descriptions)
- **Findings**: key analyst conclusions

Use this extraction template:
```
ENTITIES: [list]
IOCs:
  ips: []
  domains: []
  hashes: []
  emails: []
TTPs: [T-codes]
FINDINGS: [list]
KEY FACTS: [top 3-5 facts worth putting in hot cache]
```

### Step 4 — Create/update wiki pages

For each extracted item:

**Entities** → `wiki/entities/<Entity Name>.md`
```markdown
---
type: entity
subtype: threat-actor|malware|org|unknown
created: YYYY-MM-DD
tags: [apt, ransomware, ...]
aliases: []
origin: unknown
motivation: unknown
---

# <Entity Name>

## Overview
...

## Known IOCs
[[ioc-md5-abcd1234]]

## Known TTPs
[[T1190]]
```

**IOCs** → `wiki/iocs/<type>-<value>.md`
```markdown
---
type: ioc
ioc_type: ip|domain|hash|email|url
value: <the IOC>
created: YYYY-MM-DD
confidence: high|medium|low
tags: []
---

# <value>

## Context
...

## Associated Entities
[[Entity Name]]
```

**TTPs** → `wiki/ttps/T<number>.md` (only if not already exists)
```markdown
---
type: ttp
technique_id: T1190
name: Exploit Public-Facing Application
tactic: Initial Access
created: YYYY-MM-DD
---

# T1190 — Exploit Public-Facing Application

## Observed Usage
- [[Entity Name]]: ...
```

### Step 5 — Update housekeeping files

**wiki/sources/<slug>.md** — one-paragraph summary of the source
**wiki/index.md** — append wikilink to new pages in the relevant section
**wiki/log.md** — prepend entry:
```
### YYYY-MM-DD — Ingested <source>
- Entities: [list]
- IOCs: [count] (X IPs, Y domains, Z hashes)
- TTPs: [T-codes]
```

**wiki/hot.md** — update Key Recent Facts and Recent Changes sections with top findings.

---

## Delta Tracking

The `vault_ingest` tool uses SHA-256 to track source hashes in `.raw/.manifest.json`.
Files already ingested with same hash → skipped unless `force=true`.
This means ingest is always safe to call again.
