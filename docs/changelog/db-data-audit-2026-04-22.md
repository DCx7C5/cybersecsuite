# db/data Audit — 2026-04-22

## Duplicate fixtures removed

`data/fixtures/` contained two files identical to `src/db/fixtures/`:

| File | Action |
|------|--------|
| `data/fixtures/nist_ai_rmf.json` | Deleted (exact duplicate of `src/db/fixtures/nist_ai_rmf.json`) |
| `data/fixtures/nist_csf_2.json` | Deleted (exact duplicate of `src/db/fixtures/nist_csf_2.json`) |
| `data/fixtures/` directory | Removed (empty after deletions) |

Canonical seed fixtures live in `src/db/fixtures/` (tracked by git).
`data/` is gitignored and used only for runtime caches (downloaded full datasets).

## Runtime test data removed

`data/projects/test-project/` — gitignored runtime state with stale `tool_toggles.json`.
Deleted: not source data, no code references it by path.

## Docstrings corrected — `src/db/models/seeds.py`

6 function docstrings said `"data/fixtures/..."` but actual code reads from `src/db/fixtures/`.
Fixed all 6 docstrings to say `src/db/fixtures/`.

Affected functions: `seed_mitre_techniques`, `seed_mitre_actors`, `seed_mitre_software`,
`seed_cwe`, `seed_capec`, `seed_cve`.

## JetBrains AI context file added

Created `.jb/ai-instructions.md` — single AI context file compatible with all major
JetBrains AI plugins (AI Assistant, GitHub Copilot for JetBrains, etc.).
Contains stack, conventions, directory map, env vars, scope hierarchy.
