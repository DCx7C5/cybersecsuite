# Rename: `.ccs` → `.css` scope directory prefix

**Date:** 2026-04-22  
**Type:** refactor / breaking-rename  
**Scope:** filesystem paths, identifiers, Makefile targets, TS hooks, browser plugin

---

## Summary

The scope runtime directory prefix was incorrectly named `.ccs` (likely a typo from early scaffolding). All occurrences have been renamed to `.css` (CyberSecSuite) — including path strings, docstrings, Makefile targets, TypeScript identifiers, and browser-plugin config keys.

---

## Changes

### `Makefile`
- Target `ccs-first-setup` → `css-first-setup`
- Sentinel file `.ccs-initialized` → `.css-initialized` (6 occurrences)

### `.gitignore`
- `.ccs-initialized` → `.css-initialized`

### `src/agent_ts/hooks/ccs_first_setup.ts` → `css_first_setup.ts`
- File renamed
- Exported function `onCcsFirstSetup` → `onCssFirstSetup`
- Internal comment and `spawn("make", ["css-first-setup"])` updated

### `src/agent_ts/index.ts`
- Import path updated: `./hooks/ccs_first_setup` → `./hooks/css_first_setup`
- Usage: `onCcsFirstSetup` → `onCssFirstSetup`

### `src/browser-plugin/background.js`
- Storage key `ccs_cfg` → `css_cfg`

### `src/db/models/scope.py`
- Docstring path example `.ccs/<runtime-id>/…` → `.css/<runtime-id>/…`

### `src/db/migration/scope_v2.py`
- SQL comment path `.ccs/` → `.css/`

### `docs/configuration/scope-model.md`
- `make ccs-first-setup` → `make css-first-setup`

### `docs/agents/teams.md`
- `make ccs-first-setup` → `make css-first-setup`

### `docs/development/quickstart.md`
- `.ccs-initialized` sentinel reference → `.css-initialized`
- `make ccs-first-setup` → `make css-first-setup`

### `docs/database.md`
- ScopedEntry column path example updated

### `.jb/ai-instructions.md`
- Scope table paths updated

### `plans/plan.md`
- Scope table paths updated

---

## Migration notes

If you have an existing workspace with a `.ccs-initialized` sentinel file, rename it:

```bash
mv .ccs-initialized .css-initialized
```

If you store anything under `.ccs/<runtime-id>/`, move it:

```bash
mv .ccs .css
```

The browser plugin `ccs_cfg` key in `chrome.storage.local` has been renamed to `css_cfg`. Existing stored values will not be migrated automatically — users who have installed the plugin previously will need to re-configure it once after updating.

---

## Not changed

- `docs/changelog/scope-refactor-2026-04.md` — historical changelog, references left as-is for accuracy
- `src/db/fixtures/cve_entries.json` — contains the string `"ccs-injection"` which is a CVE tag name, unrelated to the directory prefix
