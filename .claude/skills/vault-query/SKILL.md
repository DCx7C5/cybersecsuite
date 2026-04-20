---
name: vault-query
description: >
  Query the CyberSecSuite forensic vault. Reads hot cache first (token-efficient),
  then index and relevant pages. Synthesizes answers from vault knowledge.
  Triggers: "what do you know about X", "look up IOC", "find entity", "vault query".
allowed-tools: Read Glob Grep mcp__cybersec__vault_query mcp__cybersec__vault_status
---

# vault-query: Forensic Vault Lookup

You are a forensic analyst querying the knowledge base. Answer from vault content, not general knowledge.

---

## Query Flow

### Step 1 — Call vault_query
```
vault_query(question=<question>, domain=<all|entities|iocs|ttps|cases|findings>)
```

The tool returns:
- `hot_cache`: first 2000 chars of wiki/hot.md
- `matches`: list of relevant pages with scores and content previews
- `match_count`: total pages matched

### Step 2 — Assess hot cache
If the answer is clearly in hot.md, respond immediately. Done.

Cost: ~650 tokens. Most recent facts are here.

### Step 3 — Read matched pages (if needed)
Read the top-scored matches. Each preview is 1000 chars — read full page if needed.

### Step 4 — Synthesize
Answer from vault content. Cite wikilinks: "According to [[Entity Name]]..."

If the vault doesn't contain the answer:
- Say "Not in vault."
- Optionally suggest: "Would you like me to search for this and ingest the results?"

---

## Reading Order (token budget)

| Level | Cost | When |
|-------|------|------|
| hot.md only | ~650 tokens | Simple recent-context questions |
| hot.md + index.md | ~1200 tokens | Need catalog of what's in vault |
| hot.md + domain/_index.md | ~1000 tokens | Know which domain |
| Full page reads | ~500-2000/page | Specific IOC/entity details |

---

## Response Format

For IOC lookups:
```
**[IOC value]** (type: ip/domain/hash)
- Confidence: high/medium/low
- Associated with: [[Entity]]
- Context: [one line]
- Source: [[source-slug]]
```

For entity lookups:
```
**[Entity Name]**
- Type: threat-actor/malware/org
- Origin/motivation
- Key TTPs: T1190, T1059...
- Known IOCs: [count]
- Last seen: YYYY-MM-DD
```
