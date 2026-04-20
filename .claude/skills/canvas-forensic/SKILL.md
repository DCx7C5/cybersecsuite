---
name: canvas-forensic
description: >
  Create Obsidian Canvas visual boards for forensic investigations.
  Archetypes: attack-graph, ioc-map, incident-timeline, threat-actor,
  network-topo, kill-chain (forensic) + standard: flowchart, mind-map,
  dashboard, knowledge-graph, kanban, comparison.
  Triggers: "/canvas", "create canvas", "visualize attack", "map IOCs",
  "draw timeline", "threat actor profile", "kill chain".
allowed-tools: Read Write Glob mcp__cybersec__canvas_create mcp__cybersec__canvas_list mcp__cybersec__canvas_layout mcp__cybersec__canvas_add_node mcp__cybersec__canvas_validate mcp__cybersec__canvas_archetypes mcp__cybersec__vault_query
---

# canvas-forensic: Forensic Visual Canvas Production

You create structured Obsidian Canvas files for forensic investigations. Each canvas lives in `data/vault/wiki/canvases/` and opens in Obsidian's canvas view.

---

## Forensic Archetypes

### attack-graph
MITRE ATT&CK kill chain with colored sequential nodes.
```
canvas_create(
  archetype="attack-graph",
  title="APT29 — SolarWinds Intrusion",
  data={
    "stages": [
      {"name": "Initial Access", "technique": "T1195", "detail": "Supply chain compromise via SolarWinds Orion"},
      {"name": "Execution", "technique": "T1059", "detail": "PowerShell execution"},
      ...
    ]
  }
)
```

### ioc-map
IOC network grouped by type (IP, domain, hash, email) with color zones.
```
canvas_create(
  archetype="ioc-map",
  title="Cobalt Strike Infrastructure",
  data={
    "iocs": [
      {"type": "ip", "value": "185.220.101.45", "note": "C2 server"},
      {"type": "domain", "value": "evil.example.com", "note": "Stage 1 dropper"},
      {"type": "hash", "value": "a1b2c3d4...", "note": "Beacon SHA256"},
    ]
  }
)
```

### incident-timeline
Horizontal timeline with severity-colored event nodes.
```
canvas_create(
  archetype="incident-timeline",
  title="Ransomware Incident Timeline",
  data={
    "events": [
      {"date": "2024-01-15", "event": "Phishing email delivered", "severity": "medium"},
      {"date": "2024-01-16", "event": "Credential harvesting", "severity": "high"},
      {"date": "2024-01-20", "event": "Lateral movement", "severity": "critical"},
      {"date": "2024-01-22", "event": "Ransomware deployed", "severity": "critical"},
    ]
  }
)
```

### threat-actor
Profile card grid with overview, TTPs, IOCs, campaigns, notes.
```
canvas_create(
  archetype="threat-actor",
  title="Fancy Bear Profile",
  data={
    "actor": {
      "name": "Fancy Bear",
      "aliases": ["APT28", "STRONTIUM", "Sofacy"],
      "motivation": "Espionage",
      "origin": "Russia (GRU)",
      "ttps": ["T1566", "T1078", "T1059"],
      "iocs": ["fancy-bear-c2.example.com", "192.168.1.1"],
      "campaigns": ["Operation Pawn Storm", "DNC Hack 2016"],
      "notes": "Highly sophisticated, focuses on government targets."
    }
  }
)
```

### kill-chain
7-stage Lockheed Martin kill chain framework with data per stage.
```
canvas_create(
  archetype="kill-chain",
  title="Operation X Kill Chain",
  data={
    "recon": "Spearphishing target research",
    "weaponize": "Compiled macro-laced Word doc",
    "delivery": "Phishing email",
    "exploit": "CVE-2022-30190 (Follina)",
    "install": "Cobalt Strike beacon",
    "c2": "185.220.101.45:443 HTTPS",
    "actions": "Data exfiltration via DNS tunneling"
  }
)
```

---

## Standard Archetypes

For non-forensic visual work:
- `flowchart` — process diagrams, decision trees
- `mind-map` — radial concept maps
- `dashboard` — KPI/metric layouts
- `knowledge-graph` — entity-relationship networks
- `kanban` — status board (To Do / In Progress / Done)
- `comparison` — side-by-side analysis
- `presentation` — slide-style layout

---

## After Creating

1. Call `canvas_validate` to check edge integrity.
2. Tell the user the path: `data/vault/wiki/canvases/<name>.canvas`
3. Optionally add more nodes with `canvas_add_node`.
4. To re-layout: `canvas_layout(canvas_name=..., algorithm=dagre|radial|grid)`.
